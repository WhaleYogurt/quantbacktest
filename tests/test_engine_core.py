from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from quantbacktest.core.events import MarketEvent
from quantbacktest.engine import BacktestRunner, BacktestSettings, EngineMode
from quantbacktest.strategy.base import StaticSignalStrategy
from quantbacktest.metrics.analyzer import analyze_engine_result


def _events() -> list[MarketEvent]:
    base = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    return [MarketEvent("AAPL", 100.0 + idx, base + idx * 60.0) for idx in range(5)]


def test_engine_writes_metadata(tmp_path: Path) -> None:
    settings = BacktestSettings(run_id="engine-metadata", output_dir=tmp_path, initial_cash=10_000.0)
    runner = BacktestRunner(StaticSignalStrategy(weights={"AAPL": 0.2}), settings=settings)
    result = runner.run(_events())
    assert result.status == "completed"
    assert len(result.segments) == 1
    metadata = (tmp_path / "engine-metadata" / "metadata.json")
    assert metadata.exists()
    payload = metadata.read_text()
    assert '"segments"' in payload
    metrics = analyze_engine_result(result, tmp_path / "engine-metadata")
    assert "cumulative_return" in metrics


def test_walk_forward_creates_multiple_segments(tmp_path: Path) -> None:
    settings = BacktestSettings(
        run_id="engine-wf",
        output_dir=tmp_path,
        mode=EngineMode.WALK_FORWARD,
        walk_forward_window=2,
    )
    runner = BacktestRunner(StaticSignalStrategy(weights={"AAPL": 0.3}), settings=settings)
    result = runner.run(_events())
    assert len(result.segments) >= 2
    assert all(segment.segment_id.startswith("wf-") for segment in result.segments)
