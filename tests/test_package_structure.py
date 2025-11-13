from __future__ import annotations

from pathlib import Path

import quantbacktest
from quantbacktest.engine import run_placeholder_backtest


def test_version_exposed() -> None:
    assert quantbacktest.get_version() == "0.1.0"


def test_placeholder_backtest_runs() -> None:
    result = run_placeholder_backtest(run_id="pytest")
    assert result.run_id == "pytest"
    assert result.signals > 0


def test_required_directories_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "quantbacktest" / "quantbacktest" / "data",
        root / "quantbacktest" / "quantbacktest" / "core",
        root / "quantbacktest" / "quantbacktest" / "portfolio",
        root / "quantbacktest" / "quantbacktest" / "strategy",
        root / "quantbacktest" / "quantbacktest" / "engine",
        root / "quantbacktest" / "quantbacktest" / "metrics",
        root / "quantbacktest" / "quantbacktest" / "utils",
        root / "tests" / "data",
        root / "docs",
        root / "examples",
        root / "bloat",
    ]
    for directory in required:
        assert directory.exists(), f"Missing required directory: {directory}"
