"""
Walk-forward example demonstrating EngineMode.WALK_FORWARD.
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
    parser = argparse.ArgumentParser(description="Run a walk-forward backtest example")
    parser.add_argument("--run-id", default="walk-forward-demo")
    parser.add_argument("--window", type=int, default=3, help="Window size for walk-forward segments")
    parser.add_argument("--bars", type=int, default=9, help="Number of synthetic bars to feed")
    parser.add_argument("--artifacts", default="artifacts", help="Directory for engine outputs")
    parser.add_argument("--output", default="examples/output/walk_forward.json")
    return parser.parse_args()


def make_events(bars: int) -> list[MarketEvent]:
    base = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    return [MarketEvent("AAPL", 100.0 + idx, base + idx * 60.0) for idx in range(bars)]


def main() -> None:
    args = parse_args()
    events = make_events(args.bars)
    settings = BacktestSettings(
        run_id=args.run_id,
        output_dir=Path(args.artifacts),
        mode=EngineMode.WALK_FORWARD,
        walk_forward_window=args.window,
        initial_cash=200_000.0,
    )
    runner = BacktestRunner(StaticSignalStrategy(weights={"AAPL": 0.25}), settings=settings)
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
