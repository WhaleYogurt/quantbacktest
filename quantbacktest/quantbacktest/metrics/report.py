from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..engine.modes import EngineResult
from .analyzer import analyze_engine_result


@dataclass(slots=True)
class MetricsReport:
    summary: Dict[str, float]
    segment_metrics: List[Dict[str, Any]]

    def to_markdown(self) -> str:
        header = "| Metric | Value |\n|---|---|\n"
        rows = "\n".join(f"| {key} | {value} |" for key, value in self.summary.items())
        return header + rows


def build_metrics_report(engine_result: EngineResult, output_dir: Path) -> MetricsReport:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = analyze_engine_result(engine_result, output_dir)
    segment_metrics: List[Dict[str, Any]] = []
    for segment in engine_result.segments:
        segment_metrics.append(
            {
                "segment_id": segment.segment_id,
                "fill_count": segment.fill_count,
                "duration_ms": segment.duration_ms,
                "parameters": json.dumps(segment.parameters or {}),
            }
        )
    metrics_json = {"summary": summary, "segments": segment_metrics}
    (output_dir / "metrics.json").write_text(json.dumps(metrics_json, indent=2), encoding="utf-8")
    md_path = output_dir / "metrics.md"
    md_path.write_text(build_markdown(summary, segment_metrics), encoding="utf-8")
    return MetricsReport(summary=summary, segment_metrics=segment_metrics)


def build_markdown(summary: Dict[str, float], segments: List[Dict[str, Any]]) -> str:
    md = ["# Metrics Summary", MetricsReport(summary, segments).to_markdown(), "\n## Segments"]
    for segment in segments:
        duration = float(segment.get("duration_ms", 0.0))
        md.append(
            f"- `{segment['segment_id']}`: fills={segment['fill_count']} "
            f"duration={duration:.2f} ms params={segment['parameters']}"
        )
    return "\n".join(md)
