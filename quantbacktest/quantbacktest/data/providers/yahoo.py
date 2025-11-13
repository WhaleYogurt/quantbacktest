from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]

from ..errors import DataProviderError
from .base import DataProvider, DataRequest


class YahooFinanceProvider(DataProvider):
    """Production-grade wrapper around yfinance with retries and validation."""

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
                # IMPORTANT: no group_by="ticker" → avoid MultiIndex columns
                df = yf.download(
                    request.symbol,
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                    auto_adjust=request.adjusted,
                    progress=False,
                )
                
                # Move index into a proper timestamp column
                df = df.reset_index().rename(columns={"Date": "timestamp", "Datetime": "timestamp"})
                
                if df.empty:
                    raise DataProviderError("yfinance returned no data")

                # yfinance uses either "Date" or "Datetime" depending on interval/version
                if "Date" in df.columns:
                    df = df.rename(columns={"Date": "timestamp"})
                elif "Datetime" in df.columns:
                    df = df.rename(columns={"Datetime": "timestamp"})
                else:
                    # Fallback: assume the first column is the index
                    df = df.rename(columns={df.columns[0]: "timestamp"})

                # Normalize OHLCV column names to what DataValidator expects
                rename_map = {
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Adj Close": "adj_close",
                    "Volume": "volume",
                }
                df = df.rename(columns=rename_map)

                required = ["open", "high", "low", "close", "volume"]
                missing = [col for col in required if col not in df.columns]
                if missing:
                    raise DataProviderError(f"missing column(s): {', '.join(missing)}")

                # Return only the columns DataValidator cares about.
                # DataValidator will handle timestamp normalization & sorting.
                return df[["timestamp", "open", "high", "low", "close", "volume"]]

            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.backoff * attempt)

        # If we get here, all retries failed
        raise DataProviderError(f"Yahoo Finance request failed: {last_error}")
