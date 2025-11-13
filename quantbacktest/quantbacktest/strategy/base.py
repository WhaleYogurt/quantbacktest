from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Protocol, Set

from ..core.events import MarketEvent, SignalEvent
from .context import StrategyContext


class Strategy(Protocol):
    """Interface implemented by every strategy."""

    name: str

    def on_market_data(self, event: MarketEvent) -> Iterable[SignalEvent]:
        """Process a market event and emit zero or more signals."""
        raise NotImplementedError


@dataclass
class BaseStrategy(Strategy):
    """
    Provides lifecycle helpers, warm-up enforcement, and deterministic signal handling.
    """

    name: str = "strategy"
    warmup_bars: int = 0
    max_signal_strength: float = 1.0
    min_signal_interval: float = 0.0

    context: Optional[StrategyContext] = field(default=None, init=False, repr=False)
    _processed_events: int = field(default=0, init=False, repr=False)
    _last_timestamp: Optional[float] = field(default=None, init=False, repr=False)
    _last_signal_ts: Dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _subscriptions: Set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_signal_strength <= 0:
            raise ValueError("max_signal_strength must be positive")
        if self.min_signal_interval < 0:
            raise ValueError("min_signal_interval cannot be negative")

    def set_context(self, context: StrategyContext) -> None:
        self.context = context

    def subscribe(self, *symbols: str) -> None:
        for symbol in symbols:
            self._subscriptions.add(symbol.upper())

    def on_warmup(self, event: MarketEvent) -> None:
        """Hook executed during the warm-up window."""

    def on_market_data(self, event: MarketEvent) -> Iterable[SignalEvent]:
        self._ensure_context()
        self._enforce_monotonic(event)
        if self._subscriptions and event.symbol.upper() not in self._subscriptions:
            return []

        self._processed_events += 1
        if self._processed_events <= self.warmup_bars:
            self.on_warmup(event)
            return []

        signals = list(self.generate_signals(event))
        finalized: List[SignalEvent] = []
        for signal in signals:
            if not self._allow_emission(signal.symbol, event.timestamp):
                continue
            finalized.append(self._finalize_signal(signal, event))
            self._last_signal_ts[signal.symbol] = event.timestamp

        return finalized

    def generate_signals(self, event: MarketEvent) -> Iterable[SignalEvent]:
        """Subclasses must implement the core signal generation logic."""
        raise NotImplementedError

    def create_signal(
        self,
        symbol: str,
        strength: float,
        direction: str,
        event: MarketEvent,
        signal_id: Optional[str] = None,
    ) -> SignalEvent:
        direction_norm = "LONG" if direction.upper() == "LONG" else "SHORT"
        return SignalEvent(
            symbol=symbol,
            strength=strength,
            direction=direction_norm,
            signal_id=signal_id,
            timestamp=event.timestamp,
        )

    def initialize_segment(self, segment_id: str, metadata: Dict[str, str]) -> None:
        self._processed_events = 0
        self._last_timestamp = None
        self._last_signal_ts.clear()

    @property
    def portfolio(self):
        self._ensure_context()
        return self.context.portfolio  # type: ignore[return-value]

    @property
    def indicator_cache(self):
        self._ensure_context()
        return self.context.indicator_cache  # type: ignore[return-value]

    @property
    def metadata(self) -> Dict[str, str]:
        self._ensure_context()
        return self.context.metadata or {}

    # --- internal helpers -------------------------------------------------
    def _enforce_monotonic(self, event: MarketEvent) -> None:
        if self._last_timestamp is not None and event.timestamp < self._last_timestamp:
            raise ValueError("market events must be monotonic per strategy")
        self._last_timestamp = event.timestamp

    def _allow_emission(self, symbol: str, timestamp: float) -> bool:
        if self.min_signal_interval <= 0:
            return True
        last = self._last_signal_ts.get(symbol)
        if last is None:
            return True
        return (timestamp - last) >= self.min_signal_interval

    def _finalize_signal(self, signal: SignalEvent, event: MarketEvent) -> SignalEvent:
        clamped = max(min(signal.strength, self.max_signal_strength), -self.max_signal_strength)
        signal_id = signal.signal_id or f"{self.name}-{signal.symbol}-{event.timestamp}"
        timestamp = signal.timestamp or event.timestamp
        direction_norm = "LONG" if signal.direction.upper() == "LONG" else "SHORT"
        return SignalEvent(
            symbol=signal.symbol,
            strength=clamped,
            direction=direction_norm,
            signal_id=signal_id,
            timestamp=timestamp,
        )

    def _ensure_context(self) -> None:
        if self.context is None:
            raise RuntimeError("StrategyContext has not been attached to the strategy.")


@dataclass
class StaticSignalStrategy(BaseStrategy):
    """
    Minimal reference strategy that emits static weights per symbol.
    """

    name: str = "static-signal"
    weights: Dict[str, float] = field(default_factory=dict)
    direction: str = "LONG"

    def __post_init__(self) -> None:
        super().__post_init__()

    def generate_signals(self, event: MarketEvent) -> Iterable[SignalEvent]:
        weight = self.weights.get(event.symbol, 0.0)
        if weight == 0:
            return []
        return [
            self.create_signal(
                symbol=event.symbol,
                strength=weight,
                direction=self.direction,
                event=event,
            )
        ]
