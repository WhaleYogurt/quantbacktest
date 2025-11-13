from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Iterable

from ..core.events import MarketEvent, SignalEvent
from .base import BaseStrategy


@dataclass
class AAPLMomentumStrategy(BaseStrategy):
    """
    Momentum strategy for AAPL (or any symbol) using simple price ratios.
    """

    lookback: int = 5
    threshold: float = 0.005
    weights: Dict[str, float] = field(default_factory=lambda: {"AAPL": 1.0})

    def __post_init__(self) -> None:
        super().__post_init__()
        self.warmup_bars = max(self.warmup_bars, self.lookback)
        self._history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=self.lookback))

    def initialize_segment(self, segment_id: str, metadata: Dict[str, str]) -> None:
        super().initialize_segment(segment_id, metadata)
        self._history.clear()

    def on_warmup(self, event: MarketEvent) -> None:
        self._history[event.symbol.upper()].append(event.price)

    def generate_signals(self, event: MarketEvent) -> Iterable[SignalEvent]:
        symbol = event.symbol.upper()
        history = self._history[symbol]
        history.append(event.price)
        if len(history) < self.lookback:
            return []
        base = history[0]
        if base == 0:
            return []
        momentum = history[-1] / base - 1.0
        if abs(momentum) < self.threshold:
            return []
        direction = "LONG" if momentum > 0 else "SHORT"
        strength = min(1.0, abs(momentum) / self.threshold) * self.weights.get(symbol, 1.0)
        return [
            self.create_signal(
                symbol=event.symbol,
                strength=strength,
                direction=direction,
                event=event,
                signal_id=f"{self.name}-{event.timestamp}",
            )
        ]
