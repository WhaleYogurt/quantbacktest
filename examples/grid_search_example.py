"""
Grid-search example demonstrating EngineMode.GRID_SEARCH.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from quantbacktest.core.events import MarketEvent
from quantbacktest.engine import BacktestRunner, BacktestSettings, EngineMode
from quantbacktest.strategy.base import StaticSignalStrategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a grid-search backtest example")
    parser.add_argument("--run-id", default="grid-demo")
    parser.add_argument("--bars", type=int, default=6)
    parser.add_argument(
        "--weights",
        nargs="+",
        type=float,
        default=[0.15, 0.3],
        help="Signal weights to evaluate per grid leg",
    )
    parser.add_argument("--artifacts", default="artifacts", help="Directory for engine outputs")
    parser.add_argument("--output", default="examples/output/grid_search.json")
    return parser.parse_args()


def make_events(bars: int) -> list[MarketEvent]:
    base = datetime(2020, 6, 1, tzinfo=timezone.utc).timestamp()
    return [MarketEvent("MSFT", 200.0 + idx * 0.5, base + idx * 90.0) for idx in range(bars)]


def main() -> None:
    args = parse_args()
    events = make_events(args.bars)
    grid = [{"weights": {"MSFT": weight}} for weight in args.weights]
    settings = BacktestSettings(
        run_id=args.run_id,
        output_dir=Path(args.artifacts),
        mode=EngineMode.GRID_SEARCH,
        grid_parameters=grid,
        initial_cash=150_000.0,
    )
    runner = BacktestRunner(StaticSignalStrategy(weights={"MSFT": 0.2}), settings=settings)
    result = runner.run(events)
    payload = {
        "run_id": result.run_id,
        "segments": len(result.segments),
        "metadata": result.metadata_path,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
