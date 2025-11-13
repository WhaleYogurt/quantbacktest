from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def generate_aapl(path: Path) -> None:
    rows = [
        ("timestamp", "open", "high", "low", "close", "volume"),
        ("2020-01-01", 100, 101, 99, 100.5, 1_000_000),
        ("2020-01-02", 101, 102, 100, 101.5, 1_500_000),
        ("2020-01-03", 102, 103, 101, 102.5, 1_200_000),
    ]
    write_csv(path, rows)


def write_csv(path: Path, rows: Iterable[Iterable]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)
    print(f"Wrote {path}")


def main() -> None:
    base = Path("tests") / "data"
    generate_aapl(base / "synthetic_aapl.csv")


if __name__ == "__main__":
    main()
