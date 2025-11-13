from __future__ import annotations

import argparse
import cProfile
import json
import pstats
from pathlib import Path

from ..engine import run_placeholder_backtest


def profile_placeholder_backtest(profile_file: Path) -> dict[str, int]:
    profiler = cProfile.Profile()
    profiler.enable()
    result = run_placeholder_backtest("profiling")
    profiler.disable()

    profile_file.parent.mkdir(parents=True, exist_ok=True)
    with profile_file.open("w", encoding="utf-8") as handle:
        stats = pstats.Stats(profiler, stream=handle)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats(40)
        handle.write("\nSummary\n")
        handle.write(json.dumps({"signals": result.signals}))
    return {"signals": result.signals}


def emit_hotspots(profile_file: Path, lines: int) -> str:
    payload = profile_file.read_text(encoding="utf-8").splitlines()
    preview = "\n".join(payload[:lines])
    return preview


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="quantbacktest harness utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser("profile", help="Profile placeholder backtest")
    profile_parser.add_argument("--profile-file", required=True, help="Dest path for profile.txt")

    hotspot_parser = subparsers.add_parser("hotspots", help="Emit optimization hotspots")
    hotspot_parser.add_argument("--profile-file", required=True, help="Path to profile.txt")
    hotspot_parser.add_argument("--lines", type=int, default=20, help="Number of rows to print")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    profile_path = Path(args.profile_file)
    if args.command == "profile":
        summary = profile_placeholder_backtest(profile_path)
        print(json.dumps(summary))
    elif args.command == "hotspots":
        print(emit_hotspots(profile_path, args.lines))


if __name__ == "__main__":
    main()
