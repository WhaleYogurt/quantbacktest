"""
Mean-reversion strategy example using synthetic MSFT data.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantbacktest.core.events import MarketEvent
from quantbacktest.engine import BacktestRunner, BacktestSettings
from quantbacktest.metrics.analyzer import analyze_engine_result
from quantbacktest.strategy.mean_reversion import MeanReversionStrategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mean reversion strategy example")
    parser.add_argument("--run-id", default="meanrev-demo")
    parser.add_argument("--lookback", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--output", default="examples/output/mean_reversion.json")
    return parser.parse_args()


def synthetic_msft_dataframe() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=20, freq="D", tz=timezone.utc)
    prices = pd.Series([200 + i * 0.5 + (-1) ** i * 2 for i in range(len(dates))], index=dates)
    return pd.DataFrame({"timestamp": dates, "close": prices})


def dataframe_to_events(frame: pd.DataFrame, symbol: str) -> list[MarketEvent]:
    events = []
    for row in frame.itertuples():
        ts = row.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        events.append(MarketEvent(symbol=symbol, price=float(row.close), timestamp=ts.timestamp()))
    return events


def main() -> None:
    args = parse_args()
    frame = synthetic_msft_dataframe()
    events = dataframe_to_events(frame, "MSFT")
    runner = BacktestRunner(
        strategy=MeanReversionStrategy(lookback=args.lookback, z_threshold=args.threshold, weights={"MSFT": 1.0}),
        settings=BacktestSettings(run_id=args.run_id),
    )
    result = runner.run(events)
    metrics = analyze_engine_result(result, Path("artifacts") / args.run_id)
    payload = {"run_id": args.run_id, "segments": len(result.segments), "metadata": result.metadata_path, "metrics": metrics}
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
