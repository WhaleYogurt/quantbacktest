from __future__ import annotations

from collections import defaultdict
from typing import Dict, Hashable, Iterable, MutableMapping, Optional


class IndicatorCache:
    """Simple in-memory cache for per-strategy indicator values."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[Hashable, float]] = defaultdict(dict)

    def get(self, name: str, key: Hashable) -> Optional[float]:
        return self._store.get(name, {}).get(key)

    def set(self, name: str, key: Hashable, value: float) -> float:
        self._store[name][key] = value
        return value

    def series(self, name: str) -> MutableMapping[Hashable, float]:
        return self._store.setdefault(name, {})

    def clear(self) -> None:
        self._store.clear()


def simple_moving_average(values: Iterable[float], window: int) -> float:
    series = list(values)[-window:]
    if not series or window <= 0:
        return 0.0
    return sum(series) / len(series)


def exponential_moving_average(values: Iterable[float], window: int) -> float:
    series = list(values)
    if not series or window <= 0:
        return 0.0
    alpha = 2 / (window + 1)
    ema = series[0]
    for value in series[1:]:
        ema = alpha * value + (1 - alpha) * ema
    return ema


def relative_strength_index(values: Iterable[float], window: int = 14) -> float:
    series = list(values)
    if len(series) < window + 1:
        return 50.0
    gains = []
    losses = []
    for prev, curr in zip(series[-window - 1 : -1], series[-window:]):
        change = curr - prev
        if change >= 0:
            gains.append(change)
        else:
            losses.append(abs(change))
    avg_gain = sum(gains) / window if gains else 0.0
    avg_loss = sum(losses) / window if losses else 0.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
