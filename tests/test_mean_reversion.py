from __future__ import annotations

from quantbacktest.core.events import MarketEvent
from quantbacktest.strategy.mean_reversion import MeanReversionStrategy
from quantbacktest.strategy import IndicatorCache, StrategyContext
from quantbacktest.portfolio import PortfolioState


def _context() -> StrategyContext:
    return StrategyContext(
        name="mean-rev",
        portfolio=PortfolioState(starting_cash=100_000.0),
        indicator_cache=IndicatorCache(),
        random_seed=123,
    )


def test_mean_reversion_emits_contrarian_signal() -> None:
    strategy = MeanReversionStrategy(lookback=3, z_threshold=0.1, weights={"AAPL": 1.0})
    strategy.set_context(_context())
    events = [
        MarketEvent("AAPL", 100.0, 0.0),
        MarketEvent("AAPL", 102.0, 60.0),
        MarketEvent("AAPL", 101.0, 120.0),
        MarketEvent("AAPL", 110.0, 180.0),
    ]
    signals = []
    for event in events:
        signals.extend(strategy.on_market_data(event))
    assert signals
    assert signals[-1].direction == "SHORT"
