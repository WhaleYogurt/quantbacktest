"""
AAPL momentum strategy example using the LocalCSVProvider dataset.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantbacktest.core.events import MarketEvent
from quantbacktest.data import DataRequest, DataSettings
from quantbacktest.engine import BacktestRunner, BacktestSettings, EngineMode
from quantbacktest.metrics.analyzer import analyze_engine_result
from quantbacktest.strategy.momentum import AAPLMomentumStrategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AAPL momentum strategy example")
    parser.add_argument("--run-id", default="aapl-momentum-demo")
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.005)
    parser.add_argument("--data-dir", default="tests/data")
    parser.add_argument("--cache-dir", default="cache")
    parser.add_argument("--output", default="examples/output/aapl_momentum.json")
    return parser.parse_args()


def dataframe_to_events(frame: pd.DataFrame, symbol: str) -> list[MarketEvent]:
    events = []
    for row in frame.itertuples():
        ts = row.timestamp
        if not isinstance(ts, datetime):
            ts = datetime.fromisoformat(str(ts))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        events.append(MarketEvent(symbol=symbol, price=float(row.close), timestamp=ts.timestamp()))
    return events


def main() -> None:
    args = parse_args()
    symbol = "AAPL"

    data_settings = DataSettings.defaults(cache_dir=Path(args.cache_dir), data_dir=Path(args.data_dir))
    data_manager = data_settings.build_manager()
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 12, 31, tzinfo=timezone.utc)
    frame = data_manager.fetch(DataRequest(symbol=symbol, start=start, end=end))
    events = dataframe_to_events(frame, symbol)

    runner = BacktestRunner(
        strategy=AAPLMomentumStrategy(lookback=args.lookback, threshold=args.threshold),
        settings=BacktestSettings(run_id=args.run_id, mode=EngineMode.STANDARD),
    )
    result = runner.run(events)
    metrics = analyze_engine_result(result, Path("artifacts") / args.run_id)

    payload = {
        "run_id": args.run_id,
        "segments": len(result.segments),
        "metadata": result.metadata_path,
        "metrics": metrics,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
