from __future__ import annotations

import json
from pathlib import Path

from quantbacktest.metrics.cli import main as metrics_cli_main


def test_metrics_cli_generates_summary(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.json"
    payload = {
        "run_id": "cli-demo",
        "mode": "standard",
        "status": "completed",
        "segments": [
            {
                "segment_id": "segment-1",
                "fill_count": 0,
                "duration_ms": 1.0,
                "parameters": {},
                "portfolio": {"equity": 100_000, "cash": 100_000},
            }
        ],
    }
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps(payload), encoding="utf-8")

    metrics_cli_main(["--metadata", str(metadata), "--output-dir", str(tmp_path)])
    metrics_file = tmp_path / "metrics.json"
    assert metrics_file.exists()
    data = json.loads(metrics_file.read_text())
    assert "cumulative_return" in data
