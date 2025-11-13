from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..core.events import FillEvent


@dataclass(slots=True)
class PortfolioState:
    """
    Multi-currency portfolio with trade logging and exposure summaries.
    """

    base_currency: str = "USD"
    starting_cash: float = 0.0
    cash: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    positions: Dict[str, "Position"] = field(default_factory=dict)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_fees: float = 0.0
    trade_log: List["TradeRecord"] = field(default_factory=list)
    margin_reserved: float = 0.0
    borrow_costs: float = 0.0
    equity: float = field(init=False)

    def __post_init__(self) -> None:
        self.cash.setdefault(self.base_currency, 0.0)
        if self.starting_cash:
            self.cash[self.base_currency] += self.starting_cash
        self.equity = self.total_cash()

    def deposit(self, amount: float, currency: Optional[str] = None) -> None:
        currency = currency or self.base_currency
        self.cash[currency] = self.cash.get(currency, 0.0) + amount
        self._revalue()

    def withdraw(self, amount: float, currency: Optional[str] = None) -> None:
        self.deposit(-amount, currency)

    def total_cash(self) -> float:
        return sum(self.cash.values())

    def mark_price(self, symbol: str, price: float) -> None:
        position = self.positions.get(symbol)
        if position:
            position.last_price = price
        self._revalue()

    def apply_fill(self, fill: "FillEvent", currency: Optional[str] = None) -> None:
        currency = currency or self.base_currency
        signed_qty = fill.quantity if fill.direction.upper() == "BUY" else -fill.quantity
        position = self.positions.setdefault(fill.symbol, Position(symbol=fill.symbol))
        realized = position.update(signed_qty, fill.fill_price)
        self.realized_pnl += realized
        cash_change = -signed_qty * fill.fill_price - fill.commission
        self.cash[currency] = self.cash.get(currency, 0.0) + cash_change
        self.total_fees += fill.commission
        self.trade_log.append(
            TradeRecord(
                symbol=fill.symbol,
                quantity=fill.quantity,
                direction=fill.direction,
                price=fill.fill_price,
                commission=fill.commission,
                currency=currency,
                timestamp=fill.timestamp,
            )
        )
        self._revalue()

    def reserve_margin(self, amount: float) -> None:
        self.margin_reserved += amount
        self.cash[self.base_currency] -= amount
        self._revalue()

    def release_margin(self, amount: float) -> None:
        self.margin_reserved = max(0.0, self.margin_reserved - amount)
        self.cash[self.base_currency] += amount
        self._revalue()

    def accrue_borrow_cost(self, amount: float) -> None:
        self.borrow_costs += amount
        self.cash[self.base_currency] -= amount
        self._revalue()

    def export_trades(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        header = "timestamp,symbol,quantity,direction,price,commission,currency\n"
        with path.open("w", encoding="utf-8") as handle:
            handle.write(header)
            for trade in self.trade_log:
                handle.write(
                    f"{trade.timestamp},{trade.symbol},{trade.quantity},{trade.direction},"
                    f"{trade.price},{trade.commission},{trade.currency}\n"
                )

    def _revalue(self) -> None:
        mark_to_market = 0.0
        unrealized = 0.0
        for position in self.positions.values():
            mark_to_market += position.market_value
            unrealized += position.unrealized
        self.unrealized_pnl = unrealized
        self.equity = self.total_cash() + mark_to_market - self.margin_reserved - self.borrow_costs

    def snapshot(self) -> Dict[str, float]:
        exposures = {symbol: position.quantity for symbol, position in self.positions.items()}
        summary = {
            "cash": self.total_cash(),
            "equity": self.equity,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "fees": self.total_fees,
            "margin_reserved": self.margin_reserved,
            "borrow_costs": self.borrow_costs,
        }
        summary.update({f"cash_{ccy}": amount for ccy, amount in self.cash.items()})
        summary.update(exposures)
        summary.update(self.exposure_summary())
        return summary

    def exposure_summary(self) -> Dict[str, float]:
        gross = sum(abs(position.market_value) for position in self.positions.values())
        net = sum(position.market_value for position in self.positions.values())
        leverage = gross / abs(self.equity) if self.equity else 0.0
        return {"gross_exposure": gross, "net_exposure": net, "leverage": leverage}

    def position(self, symbol: str) -> "Position":
        return self.positions.setdefault(symbol, Position(symbol=symbol))


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: int = 0
    avg_cost: float = 0.0
    last_price: float = 0.0
    realized_pnl: float = 0.0

    def update(self, delta: int, price: float) -> float:
        if delta == 0:
            return 0.0

        pnl = 0.0
        if self.quantity == 0 or (self.quantity > 0 and delta > 0) or (self.quantity < 0 and delta < 0):
            total_cost = self.avg_cost * self.quantity + price * delta
            self.quantity += delta
            self.avg_cost = total_cost / self.quantity if self.quantity != 0 else 0.0
        else:
            closing_qty = min(abs(delta), abs(self.quantity))
            if self.quantity > 0:
                pnl = closing_qty * (price - self.avg_cost)
            else:
                pnl = closing_qty * (self.avg_cost - price)

            self.quantity += delta
            if self.quantity == 0:
                self.avg_cost = 0.0
            elif (self.quantity > 0 and delta > 0) or (self.quantity < 0 and delta < 0):
                self.avg_cost = price

        self.last_price = price
        self.realized_pnl += pnl
        return pnl

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price

    @property
    def unrealized(self) -> float:
        return self.quantity * (self.last_price - self.avg_cost)


@dataclass(slots=True)
class TradeRecord:
    symbol: str
    quantity: int
    direction: str
    price: float
    commission: float
    currency: str
    timestamp: Optional[float] = None
