from __future__ import annotations

from quantbacktest.strategy.indicators import (
    IndicatorCache,
    exponential_moving_average,
    relative_strength_index,
    simple_moving_average,
)


def test_indicator_cache_roundtrip() -> None:
    cache = IndicatorCache()
    cache.set("sma", "AAPL", 1.23)
    assert cache.get("sma", "AAPL") == 1.23
    cache.clear()
    assert cache.get("sma", "AAPL") is None


def test_moving_averages() -> None:
    values = [1, 2, 3, 4, 5]
    assert simple_moving_average(values, 3) == 4.0
    ema = exponential_moving_average(values, 3)
    assert ema > 0


def test_relative_strength_index() -> None:
    values = list(range(1, 20))
    rsi = relative_strength_index(values, window=5)
    assert 0 <= rsi <= 100
