from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..engine.modes import EngineResult
from .base import compute_basic_metrics
from .ratios import sharpe_ratio, sortino_ratio


def analyze_engine_result(engine_result: EngineResult, output_dir: Path | None = None) -> Dict[str, float]:
    returns = _derive_returns(engine_result)
    report = compute_basic_metrics(returns)
    summary = {
        "cumulative_return": report.cumulative_return,
        "average_return": report.average_return,
        "annualized_return": report.annualized_return,
        "max_drawdown": report.max_drawdown,
        "sharpe": sharpe_ratio(returns),
        "sortino": sortino_ratio(returns),
        "segments": len(engine_result.segments),
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _derive_returns(engine_result: EngineResult) -> List[float]:
    returns: List[float] = []
    for segment in engine_result.segments:
        snapshot = segment.portfolio_snapshot
        equity = snapshot.get("equity", 0.0)
        cash = snapshot.get("cash", 0.0)
        if not returns:
            returns.append((equity - cash) / (cash or 1.0))
        else:
            prev_equity = returns[-1] + 1.0
            returns.append(equity / prev_equity - 1.0)
    return returns or [0.0]
