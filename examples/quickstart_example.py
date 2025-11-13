"""
Minimal example that exercises the placeholder backtest runner.

Usage:
    python examples/quickstart_example.py --test-mode
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quantbacktest.engine import run_placeholder_backtest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="quantbacktest quickstart example")
    parser.add_argument("--run-id", default="example", help="Identifier for metadata logging")
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable deterministic, low-cost execution for CI.",
    )
    parser.add_argument(
        "--output",
        default="examples/output.json",
        help="Where to persist the summarized results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_placeholder_backtest(run_id=args.run_id)
    payload = {"run_id": result.run_id, "signals": result.signals, "test_mode": args.test_mode}
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
