from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import pandas as pd


@dataclass(slots=True)
class DataRequest:
    symbol: str
    start: datetime
    end: datetime
    interval: str = "1d"
    adjusted: bool = True

    def cache_key(self) -> str:
        start_key = self.start.strftime("%Y%m%d")
        end_key = self.end.strftime("%Y%m%d")
        adj = "adj" if self.adjusted else "raw"
        return f"{self.symbol.upper()}_{self.interval}_{adj}_{start_key}_{end_key}"


class DataProvider(Protocol):
    """Interface implemented by every market data provider."""

    name: str

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        """Retrieve raw market data as a pandas DataFrame."""
        raise NotImplementedError
