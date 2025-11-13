from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]

from ..errors import DataProviderError
from .base import DataProvider, DataRequest


class YahooFinanceProvider(DataProvider):
    """Robust wrapper around yfinance that normalizes output for the data validator."""

    name = "yahoo"

    def __init__(self, retries: int = 3, backoff: float = 1.0) -> None:
        self.retries = retries
        self.backoff = backoff

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        if not isinstance(request.start, datetime) or not isinstance(request.end, datetime):
            raise TypeError("start/end must be datetime instances")
        if request.start >= request.end:
            raise ValueError("start must be earlier than end")

        last_error: Optional[Exception] = None

        for attempt in range(1, self.retries + 1):
            try:
                df = yf.download(
                    request.symbol,
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                    auto_adjust=request.adjusted,
                    progress=False,
                )

                if df.empty:
                    raise DataProviderError("yfinance returned no data")

                # Put the index into a regular column
                df = df.reset_index()

                # ---- 1) Normalize column names (flatten everything & lowercase) ----
                flat_cols = []
                for col in df.columns:
                    # MultiIndex columns or weird objects
                    if isinstance(col, tuple):
                        parts = [str(p).strip() for p in col if p not in (None, "", " ")]
                        name = "_".join(parts) if parts else str(col)
                    else:
                        name = str(col).strip()
                    flat_cols.append(name.lower())
                df.columns = flat_cols

                # ---- 2) Find timestamp column ----
                ts_candidates = [
                    c
                    for c in df.columns
                    if "date" in c or "time" in c or "stamp" in c
                ]
                if not ts_candidates:
                    # If we can't find one by name, assume the first column is the timestamp
                    ts_col = df.columns[0]
                else:
                    ts_col = ts_candidates[0]

                if ts_col != "timestamp":
                    df = df.rename(columns={ts_col: "timestamp"})

                # ---- 3) Find OHLCV columns by substring match ----
                logical_to_physical: dict[str, str] = {}
                missing_logicals: list[str] = []

                for logical in ("open", "high", "low", "close", "volume"):
                    matches = [
                        c
                        for c in df.columns
                        if c != "timestamp" and logical in c
                    ]
                    if matches:
                        logical_to_physical[logical] = matches[0]
                    else:
                        missing_logicals.append(logical)

                if missing_logicals:
                    raise DataProviderError(
                        f"missing columns: {', '.join(missing_logicals)}"
                    )

                # ---- 4) Rename physical → logical names ----
                for logical, physical in logical_to_physical.items():
                    if logical != physical:
                        df = df.rename(columns={physical: logical})

                # ---- 5) Return exactly what the validator expects ----
                return df[["timestamp", "open", "high", "low", "close", "volume"]]

            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.backoff * attempt)

        raise DataProviderError(f"Yahoo Finance request failed: {last_error}")
