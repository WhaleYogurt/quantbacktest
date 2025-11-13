from __future__ import annotations

import pytest

from quantbacktest.core.events import MarketEvent, OrderEvent
from quantbacktest.core.execution import (
    CommissionModel,
    ExecutionConfig,
    SimulatedExecutionHandler,
    SlippageModel,
    SpreadModel,
)


def test_market_order_slippage_and_commission() -> None:
    config = ExecutionConfig(
        slippage=SlippageModel(bps=10.0),
        spread=SpreadModel(bps=0.0),
        commissions=CommissionModel(per_share=0.01),
    )
    handler = SimulatedExecutionHandler(config)
    order = OrderEvent(order_id="ord-1", symbol="AAPL", quantity=100, direction="BUY")
    market = MarketEvent(symbol="AAPL", price=100.0, timestamp=1.0)
    fills = handler.execute(order, market)
    assert len(fills) == 1
    fill = fills[0]
    assert fill.fill_price == pytest.approx(100.1)
    assert fill.commission == pytest.approx(1.0)


def test_limit_order_not_filled_when_price_not_reached() -> None:
    handler = SimulatedExecutionHandler(
        ExecutionConfig(slippage=SlippageModel(bps=0.0), spread=SpreadModel(bps=0.0))
    )
    order = OrderEvent(
        order_id="ord-2",
        symbol="AAPL",
        quantity=50,
        direction="BUY",
        order_type="LIMIT",
        limit_price=95.0,
    )
    market = MarketEvent(symbol="AAPL", price=100.0, timestamp=2.0)
    assert handler.execute(order, market) == []


def test_sell_limit_order_fills_at_limit() -> None:
    handler = SimulatedExecutionHandler(
        ExecutionConfig(slippage=SlippageModel(bps=0.0), spread=SpreadModel(bps=0.0))
    )
    order = OrderEvent(
        order_id="ord-3",
        symbol="MSFT",
        quantity=25,
        direction="SELL",
        order_type="LIMIT",
        limit_price=300.0,
    )
    market = MarketEvent(symbol="MSFT", price=305.0, timestamp=3.0)
    fills = handler.execute(order, market)
    assert fills and fills[0].fill_price == pytest.approx(300.0)


def test_partial_fill_behavior() -> None:
    handler = SimulatedExecutionHandler(
        ExecutionConfig(
            slippage=SlippageModel(bps=0.0),
            spread=SpreadModel(bps=0.0),
            partial_fill_ratio=0.5,
        )
    )
    order = OrderEvent(order_id="ord-4", symbol="AAPL", quantity=10, direction="BUY")
    market = MarketEvent(symbol="AAPL", price=50.0, timestamp=4.0)
    fills = handler.execute(order, market)
    assert len(fills) >= 2
    total_qty = sum(fill.quantity for fill in fills)
    assert total_qty == 10
