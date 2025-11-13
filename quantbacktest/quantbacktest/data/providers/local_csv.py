from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..errors import DataProviderError
from .base import DataProvider, DataRequest


class LocalCSVProvider(DataProvider):
    """
    Loads deterministic offline datasets from disk.

    Intended for tests and air-gapped research environments.
    """

    name = "local-csv"

    def __init__(self, data_dir: Path, pattern: str = "synthetic_{symbol}.csv") -> None:
        self.data_dir = data_dir
        self.pattern = pattern

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        symbol_slug = request.symbol.lower()
        filename = self.pattern.format(symbol=symbol_slug, interval=request.interval)
        path = self.data_dir / filename
        if not path.exists():
            raise DataProviderError(f"local fixture missing: {path}")
        frame = pd.read_csv(path)
        if "timestamp" not in frame.columns and "date" in frame.columns:
            frame = frame.rename(columns={"date": "timestamp"})
        return frame
