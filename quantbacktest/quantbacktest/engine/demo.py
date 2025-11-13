from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from ..core.events import MarketEvent
from ..strategy.base import StaticSignalStrategy
from .base import BacktestRunner, BacktestSettings


@dataclass(slots=True)
class PlaceholderResult:
    run_id: str
    signals: int


def run_placeholder_backtest(run_id: str = "skeleton") -> PlaceholderResult:
    """
    Execute a deterministic, low-cost backtest used by Step 1 testing.

    The result object is intentionally tiny so tests can assert on it without
    coupling to future engine internals.
    """

    runner = BacktestRunner(
        StaticSignalStrategy(weights={"AAPL": 1.0}),
        settings=BacktestSettings(run_id=run_id),
    )
    base_ts = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    events: List[MarketEvent] = [
        MarketEvent("AAPL", 100.0 + idx, base_ts + idx * 60.0) for idx in range(3)
    ]
    engine_result = runner.run(events)
    fills = sum(segment.fill_count for segment in engine_result.segments)
    return PlaceholderResult(run_id=run_id, signals=fills)
