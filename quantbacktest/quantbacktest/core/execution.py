from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .events import FillEvent, MarketEvent, OrderEvent


@dataclass(slots=True)
class SlippageModel:
    bps: float = 1.0

    def adjust(self, price: float, direction: str) -> float:
        adjust = self.bps / 10_000
        return price * (1 + adjust) if direction == "BUY" else price * (1 - adjust)


@dataclass(slots=True)
class SpreadModel:
    bps: float = 0.5

    def bid_ask(self, mid: float) -> tuple[float, float]:
        half = (self.bps / 10_000) * mid
        return mid - half, mid + half


@dataclass(slots=True)
class CommissionModel:
    per_share: float = 0.0

    def cost(self, quantity: int) -> float:
        return abs(quantity) * self.per_share


@dataclass(slots=True)
class ExecutionConfig:
    slippage: SlippageModel = field(default_factory=SlippageModel)
    spread: SpreadModel = field(default_factory=SpreadModel)
    commissions: CommissionModel = field(default_factory=CommissionModel)
    fill_on_limit_touch: bool = True
    partial_fill_ratio: float = 1.0  # 0-1 fraction filled per event


class ExecutionHandler:
    """Interface for execution backends."""

    def execute(self, order: OrderEvent, market: MarketEvent) -> List[FillEvent]:
        raise NotImplementedError


class SimulatedExecutionHandler(ExecutionHandler):
    """
    Deterministic execution model with configurable slippage/spread/commission assumptions.
    Supports partial fills using `partial_fill_ratio`.
    """

    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def execute(self, order: OrderEvent, market: MarketEvent) -> List[FillEvent]:
        if market.symbol != order.symbol:
            return []

        execution_price = self._price_with_limit_checks(order, market.price)
        if execution_price is None:
            return []

        fills: List[FillEvent] = []
        remaining = order.quantity
        while remaining > 0:
            fill_qty = max(1, int(remaining * self.config.partial_fill_ratio))
            fill_qty = min(fill_qty, remaining)
            price = self._apply_transaction_costs(order.direction, execution_price)
            commission = self.config.commissions.cost(fill_qty)
            fills.append(
                FillEvent(
                    order_id=order.order_id,
                    symbol=order.symbol,
                    quantity=fill_qty,
                    direction=order.direction,
                    fill_price=price,
                    commission=commission,
                    slippage_bps=self.config.slippage.bps,
                    spread_bps=self.config.spread.bps,
                    timestamp=market.timestamp,
                )
            )
            remaining -= fill_qty
            if self.config.partial_fill_ratio >= 1.0:
                break
        return fills

    def _price_with_limit_checks(self, order: OrderEvent, market_price: float) -> Optional[float]:
        bid, ask = self.config.spread.bid_ask(market_price)
        if order.order_type == "MARKET":
            return ask if order.direction == "BUY" else bid

        if order.limit_price is None:
            return None

        if order.direction == "BUY":
            if market_price < order.limit_price or (
                self.config.fill_on_limit_touch and market_price <= order.limit_price
            ):
                return order.limit_price
        else:  # SELL
            if market_price > order.limit_price or (
                self.config.fill_on_limit_touch and market_price >= order.limit_price
            ):
                return order.limit_price
        return None

    def _apply_transaction_costs(self, direction: str, price: float) -> float:
        return self.config.slippage.adjust(price, direction)
