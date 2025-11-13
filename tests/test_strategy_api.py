from __future__ import annotations

from dataclasses import dataclass

from quantbacktest.core.events import MarketEvent, SignalEvent
from quantbacktest.portfolio import PortfolioState
from quantbacktest.strategy import BaseStrategy, IndicatorCache, StrategyContext


def _context() -> StrategyContext:
    return StrategyContext(
        name="test",
        portfolio=PortfolioState(starting_cash=100_000.0),
        indicator_cache=IndicatorCache(),
        random_seed=42,
        metadata={"suite": "unit"},
    )


@dataclass
class EchoStrategy(BaseStrategy):
    def generate_signals(self, event: MarketEvent):
        yield self.create_signal(event.symbol, 2.0, "LONG", event)


def test_warmup_prevents_signals_until_ready() -> None:
    strategy = EchoStrategy(name="echo", warmup_bars=2)
    strategy.set_context(_context())
    events = [
        MarketEvent("AAPL", 100.0, 0.0),
        MarketEvent("AAPL", 101.0, 60.0),
        MarketEvent("AAPL", 102.0, 120.0),
    ]
    outputs = [strategy.on_market_data(evt) for evt in events]
    assert outputs[0] == []
    assert outputs[1] == []
    assert len(outputs[2]) == 1


def test_signal_clamping_and_interval_guard() -> None:
    strategy = EchoStrategy(name="clamp", max_signal_strength=0.5, min_signal_interval=60.0)
    strategy.set_context(_context())
    first = strategy.on_market_data(MarketEvent("MSFT", 200.0, 0.0))
    assert first[0].strength == 0.5
    second = strategy.on_market_data(MarketEvent("MSFT", 201.0, 30.0))
    assert second == []
    third = strategy.on_market_data(MarketEvent("MSFT", 202.0, 90.0))
    assert len(third) == 1


def test_indicator_cache_accessible_via_context() -> None:
    strategy = EchoStrategy(name="cache")
    context = _context()
    strategy.set_context(context)
    strategy.indicator_cache.set("rsi", 0, 55.0)
    assert strategy.indicator_cache.get("rsi", 0) == 55.0
