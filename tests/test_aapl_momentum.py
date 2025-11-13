from __future__ import annotations

from quantbacktest.core.events import MarketEvent
from quantbacktest.portfolio import PortfolioState
from quantbacktest.strategy import AAPLMomentumStrategy, IndicatorCache, StrategyContext


def _context() -> StrategyContext:
    return StrategyContext(
        name="test",
        portfolio=PortfolioState(starting_cash=100_000),
        indicator_cache=IndicatorCache(),
        random_seed=42,
    )


def test_aapl_momentum_generates_long_signal() -> None:
    strategy = AAPLMomentumStrategy(lookback=3, threshold=0.01)
    strategy.set_context(_context())
    events = [
        MarketEvent("AAPL", 100.0, 0.0),
        MarketEvent("AAPL", 101.0, 60.0),
        MarketEvent("AAPL", 102.0, 120.0),
        MarketEvent("AAPL", 105.0, 180.0),
    ]
    signals = []
    for event in events:
        signals.extend(strategy.on_market_data(event))
    assert signals
    assert signals[-1].direction == "LONG"
