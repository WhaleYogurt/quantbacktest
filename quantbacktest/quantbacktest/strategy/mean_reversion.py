from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Iterable

from ..core.events import MarketEvent, SignalEvent
from .base import BaseStrategy
from .indicators import simple_moving_average


@dataclass
class MeanReversionStrategy(BaseStrategy):
    """
    Emits contrarian signals when price deviates from its moving average.
    """

    lookback: int = 10
    z_threshold: float = 1.0
    weights: Dict[str, float] = field(default_factory=lambda: {"AAPL": 1.0})

    def __post_init__(self) -> None:
        super().__post_init__()
        self.warmup_bars = max(self.warmup_bars, self.lookback)
        self._history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=self.lookback))

    def on_warmup(self, event: MarketEvent) -> None:
        self._history[event.symbol].append(event.price)

    def generate_signals(self, event: MarketEvent) -> Iterable[SignalEvent]:
        series = self._history[event.symbol]
        series.append(event.price)
        if len(series) < self.lookback:
            return []
        mean = simple_moving_average(series, self.lookback)
        variance = sum((price - mean) ** 2 for price in series) / self.lookback
        std = variance ** 0.5
        if std == 0:
            return []
        z_score = (series[-1] - mean) / std
        if abs(z_score) < self.z_threshold:
            return []
        direction = "SHORT" if z_score > 0 else "LONG"
        strength = min(1.0, abs(z_score) / self.z_threshold) * self.weights.get(event.symbol, 1.0)
        return [
            self.create_signal(
                symbol=event.symbol,
                strength=strength,
                direction=direction,
                event=event,
                signal_id=f"{self.name}-{event.timestamp}",
            )
        ]
