from __future__ import annotations

from pathlib import Path

from quantbacktest.engine.modes import EngineMode, EngineResult, EngineSegmentResult
from quantbacktest.metrics.report import build_metrics_report


def test_build_metrics_report_writes_files(tmp_path: Path) -> None:
    segments = [
        EngineSegmentResult(
            segment_id="seg-1",
            fills=[],
            portfolio_snapshot={"equity": 100_000, "cash": 100_000},
            parameters={"foo": 1},
            duration_ms=5.0,
        )
    ]
    result = EngineResult(
        run_id="report-demo",
        mode=EngineMode.STANDARD,
        segments=segments,
        metadata_path=str(tmp_path / "metadata.json"),
        status="completed",
    )
    report = build_metrics_report(result, tmp_path)
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "metrics.md").exists()
    assert "cumulative_return" in report.summary
