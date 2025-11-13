from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

import pandas as pd

from .errors import DataValidationError
from .providers.base import DataRequest


@dataclass(slots=True)
class DataValidator:
    required_columns: Iterable[str] = field(
        default_factory=lambda: ("timestamp", "open", "high", "low", "close", "volume")
    )

    def validate(self, frame: pd.DataFrame, request: DataRequest) -> pd.DataFrame:
        if frame is None or frame.empty:
            raise DataValidationError("received empty data frame")

        df = frame.copy()

        # --- Normalize column names: handle both Index and MultiIndex ---
        if isinstance(df.columns, pd.MultiIndex):
            normalized_cols = []
            for col in df.columns:
                # For a MultiIndex column, pick the last non-empty level as the base name.
                # Example: ('AAPL', 'Close') -> 'close'
                if isinstance(col, tuple):
                    parts = [p for p in col if p not in (None, "", " ")]
                    base = parts[-1] if parts else col[-1]
                else:
                    base = col
                normalized_cols.append(str(base).lower())
            df.columns = normalized_cols
        else:
            df.columns = [str(col).lower() for col in df.columns]

        required_cols = list(self.required_columns)
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise DataValidationError(f"missing columns: {', '.join(missing)}")

        # Normalize timestamps to UTC and ensure monotonicity
        df["timestamp"] = _normalize_timestamps(df["timestamp"])
        if df["timestamp"].duplicated().any():
            raise DataValidationError("duplicate timestamps detected")

        if not df["timestamp"].is_monotonic_increasing:
            df = df.sort_values("timestamp", ignore_index=True)

        # Ensure no NaNs in required columns
        if df[required_cols].isna().any().any():
            raise DataValidationError("NaN values detected in required columns")

        # Enforce requested date range (no look-ahead / leakage)
        request_start = _ensure_utc(request.start)
        request_end = _ensure_utc(request.end)

        if df["timestamp"].min() < request_start:
            raise DataValidationError("data begins before request start; potential leakage")
        if df["timestamp"].max() > request_end:
            raise DataValidationError("data extends beyond request end; potential lookahead")

        df = df[(df["timestamp"] >= request_start) & (df["timestamp"] <= request_end)].reset_index(drop=True)
        return df


def _normalize_timestamps(series: pd.Series) -> pd.Series:
    timestamps = pd.to_datetime(series, utc=True)
    # Ensure everything is timezone-aware UTC
    if timestamps.dt.tz is not None:
        return timestamps.dt.tz_convert(timezone.utc)
    return timestamps


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
