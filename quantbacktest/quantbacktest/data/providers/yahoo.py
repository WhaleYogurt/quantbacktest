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
                df = yf.download(
                    request.symbol,
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                    auto_adjust=request.adjusted,
                    progress=False,
                    group_by="ticker",
                )
                if df.empty:
                    raise DataProviderError("yfinance returned no data")
                df = df.reset_index(names="timestamp")
                rename_map = {
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Adj Close": "adj_close",
                    "Volume": "volume",
                }
                df = df.rename(columns=rename_map)
                missing = [col for col in ["open", "high", "low", "close", "volume"] if col not in df.columns]
                if missing:
                    raise DataProviderError(f"missing column(s): {', '.join(missing)}")
                return df
            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                if attempt < self.retries:
                    time.sleep(self.backoff * attempt)
        raise DataProviderError(f"Yahoo Finance request failed: {last_error}")
