from __future__ import annotations

from pathlib import Path

DOC_FILES = [
    "docs/quickstart.md",
    "docs/architecture.md",
    "docs/strategies.md",
    "docs/data.md",
    "docs/metrics.md",
    "docs/examples.md",
    "docs/ci.md",
]


def test_docs_exist_and_nonempty() -> None:
    for rel_path in DOC_FILES:
        path = Path(rel_path)
        assert path.exists(), f"{rel_path} missing"
        text = path.read_text(encoding="utf-8").strip()
        assert len(text) > 200, f"{rel_path} too short"
