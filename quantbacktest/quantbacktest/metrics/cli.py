from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..engine.modes import EngineMode, EngineResult, EngineSegmentResult
from .analyzer import analyze_engine_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="quantbacktest metrics analyzer CLI")
    parser.add_argument("--metadata", required=True, help="Path to engine metadata.json")
    parser.add_argument("--output-dir", help="Optional directory to persist metrics.json")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    metadata_path = Path(args.metadata)
    payload = json.loads(metadata_path.read_text())
    segments = []
    for seg in payload.get("segments", []):
        segments.append(
            EngineSegmentResult(
                segment_id=seg["segment_id"],
                fills=[],
                portfolio_snapshot=seg.get("portfolio", {}),
                parameters=seg.get("parameters"),
                duration_ms=seg.get("duration_ms", 0.0),
            )
        )
    result = EngineResult(
        run_id=payload["run_id"],
        mode=EngineMode(payload.get("mode", "standard")),
        segments=segments,
        metadata_path=str(metadata_path),
        status=payload.get("status", "completed"),
    )
    output_dir = Path(args.output_dir) if args.output_dir else metadata_path.parent
    summary = analyze_engine_result(result, output_dir)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
