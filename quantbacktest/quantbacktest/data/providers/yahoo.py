from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]

from ..errors import DataProviderError
from .base import DataProvider, DataRequest


class YahooFinanceProvider(DataProvider):
    """Wrapper around yfinance that normalizes output for the data validator."""

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

                # Move index into a column
                df = df.reset_index()

                # --- Normalize timestamp column name ---
                # yfinance usually uses "Date" or "Datetime"
                ts_candidates = [
                    c
                    for c in df.columns
                    if str(c).lower() in ("date", "datetime", "timestamp")
                ]
                if ts_candidates:
                    ts_col = ts_candidates[0]
                else:
                    # Fallback: assume the first column is the datetime index
                    ts_col = df.columns[0]

                df = df.rename(columns={ts_col: "timestamp"})

                # --- Flatten and lowercase all non-timestamp columns ---
                new_cols = []
                for col in df.columns:
                    if col == "timestamp":
                        new_cols.append("timestamp")
                        continue

                    if isinstance(col, tuple):
                        parts = [p for p in col if p not in (None, "", " ")]
                        base = parts[-1] if parts else col[-1]
                    else:
                        base = col
                    new_cols.append(str(base).lower())

                df.columns = new_cols

                # --- Map whatever yfinance gave us to standard OHLCV names ---
                logical_to_physical: dict[str, str] = {}
                missing_logicals: list[str] = []

                for logical in ["open", "high", "low", "close", "volume"]:
                    matches = [
                        c
                        for c in df.columns
                        if c == logical
                        or c.endswith(" " + logical)
                        or c.endswith("_" + logical)
                    ]
                    if matches:
                        logical_to_physical[logical] = matches[0]
                    else:
                        missing_logicals.append(logical)

                if missing_logicals:
                    raise DataProviderError(
                        f"missing columns: {', '.join(missing_logicals)}"
                    )

                # Rename physical -> logical to standardize
                for logical, physical in logical_to_physical.items():
                    if logical != physical:
                        df = df.rename(columns={physical: logical})

                # Keep only what the validator expects
                return df[["timestamp", "open", "high", "low", "close", "volume"]]

            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.backoff * attempt)

        raise DataProviderError(f"Yahoo Finance request failed: {last_error}")
