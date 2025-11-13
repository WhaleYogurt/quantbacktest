from __future__ import annotations

from pathlib import Path

from quantbacktest.core.events import FillEvent
from quantbacktest.portfolio import PortfolioState


def _fill(symbol: str, quantity: int, direction: str, price: float, commission: float = 0.0) -> FillEvent:
    return FillEvent(
        order_id="ord-test",
        symbol=symbol,
        quantity=quantity,
        direction=direction,
        fill_price=price,
        commission=commission,
    )


def test_apply_fill_and_mark_price_updates_cash_and_equity() -> None:
    portfolio = PortfolioState(starting_cash=100_000.0)
    buy_fill = _fill("AAPL", 100, "BUY", 100.0, commission=1.0)
    portfolio.apply_fill(buy_fill)
    assert portfolio.cash[portfolio.base_currency] == 100_000.0 - (100 * 100.0) - 1.0
    assert portfolio.positions["AAPL"].quantity == 100

    portfolio.mark_price("AAPL", 105.0)
    snapshot = portfolio.snapshot()
    assert snapshot["equity"] == portfolio.total_cash() + 100 * 105.0
    assert snapshot["unrealized_pnl"] == 100 * (105.0 - 100.0)


def test_realized_pnl_on_position_close() -> None:
    portfolio = PortfolioState(starting_cash=50_000.0)
    portfolio.apply_fill(_fill("MSFT", 50, "BUY", 200.0))
    portfolio.apply_fill(_fill("MSFT", 30, "SELL", 210.0))
    assert portfolio.positions["MSFT"].quantity == 20
    assert portfolio.realized_pnl == 30 * (210.0 - 200.0)


def test_exposure_summary_reports_gross_and_net() -> None:
    portfolio = PortfolioState(starting_cash=500_000.0)
    portfolio.apply_fill(_fill("SPY", 100, "BUY", 400.0))
    portfolio.mark_price("SPY", 405.0)
    summary = portfolio.exposure_summary()
    assert summary["gross_exposure"] == abs(100 * 405.0)
    assert summary["net_exposure"] == 100 * 405.0


def test_margin_and_trade_export(tmp_path: Path) -> None:
    portfolio = PortfolioState(starting_cash=200_000.0)
    portfolio.reserve_margin(10_000.0)
    assert portfolio.margin_reserved == 10_000.0
    portfolio.release_margin(5_000.0)
    assert portfolio.margin_reserved == 5_000.0
    portfolio.accrue_borrow_cost(500.0)
    assert portfolio.borrow_costs == 500.0
    portfolio.apply_fill(_fill("QQQ", 10, "BUY", 100.0))
    export_path = tmp_path / "trades.csv"
    portfolio.export_trades(export_path)
    content = export_path.read_text()
    assert "QQQ" in content
