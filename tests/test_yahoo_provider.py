from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from quantbacktest.data.providers.base import DataRequest
from quantbacktest.data.providers.yahoo import YahooFinanceProvider


def test_yahoo_provider_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = YahooFinanceProvider(retries=1)
    fake_df = pd.DataFrame(
        {
            "Open": [100, 101],
            "High": [101, 102],
            "Low": [99, 100],
            "Close": [100.5, 101.5],
            "Adj Close": [100.5, 101.5],
            "Volume": [1_000_000, 1_200_000],
        }
    )
    fake_df.index = pd.DatetimeIndex([datetime(2020, 1, 1), datetime(2020, 1, 2)], name="Date")

    def fake_download(*args, **kwargs):
        return fake_df.copy()

    monkeypatch.setattr("quantbacktest.data.providers.yahoo.yf.download", fake_download)
    result = provider.fetch(
        DataRequest(
            symbol="AAPL",
            start=datetime(2020, 1, 1, tzinfo=timezone.utc),
            end=datetime(2020, 1, 3, tzinfo=timezone.utc),
        )
    )
    assert "open" in result.columns
    assert len(result) == 2
