from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from quantbacktest.data import (
    DataManager,
    DataRequest,
    DataSettings,
    DataValidator,
    LocalCSVProvider,
    LocalDataCache,
)
from quantbacktest.data.errors import DataFetchError, DataProviderError, DataValidationError
from quantbacktest.data.providers.yahoo import YahooFinanceProvider


class FailingProvider:
    name = "failing"

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        raise DataProviderError("forced failure")


class StubProvider:
    name = "stub"

    def __init__(self, frame: pd.DataFrame) -> None:
        self.frame = frame
        self.calls = 0

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        self.calls += 1
        return self.frame


def _request() -> DataRequest:
    return DataRequest(
        symbol="AAPL",
        start=datetime(2020, 1, 1, tzinfo=timezone.utc),
        end=datetime(2020, 1, 3, tzinfo=timezone.utc),
        interval="1d",
    )


def test_data_manager_uses_cache_before_providers(tmp_path: Path) -> None:
    cache = LocalDataCache(root=tmp_path / "cache")
    request = _request()

    cached_frame = pd.DataFrame(
        {
            "timestamp": [
                datetime(2020, 1, 1, tzinfo=timezone.utc),
                datetime(2020, 1, 2, tzinfo=timezone.utc),
            ],
            "open": [1.0, 1.5],
            "high": [1.1, 1.6],
            "low": [0.9, 1.4],
            "close": [1.05, 1.55],
            "volume": [1.0, 2.0],
        }
    )
    cache.store_frame(request.cache_key(), cached_frame)
    provider = StubProvider(cached_frame)

    manager = DataManager(cache=cache, providers=[provider])
    frame = manager.fetch(request)
    assert len(frame) == 2
    assert provider.calls == 0


def test_data_manager_falls_back_across_providers(tmp_path: Path) -> None:
    cache = LocalDataCache(root=tmp_path / "cache")
    request = _request()

    good_frame = pd.DataFrame(
        {
            "timestamp": [
                datetime(2020, 1, 1, tzinfo=timezone.utc),
                datetime(2020, 1, 2, tzinfo=timezone.utc),
                datetime(2020, 1, 3, tzinfo=timezone.utc),
            ],
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100.5, 101.5, 102.5],
            "volume": [1_000_000, 1_200_000, 1_300_000],
        }
    )

    stub = StubProvider(good_frame)
    manager = DataManager(cache=cache, providers=[FailingProvider(), stub])
    result = manager.fetch(request)
    assert len(result) == 3
    assert stub.calls == 1

    # second fetch should hit cache instead of stub
    result = manager.fetch(request)
    assert stub.calls == 1
    assert len(result) == 3


def test_validator_detects_duplicates() -> None:
    validator = DataValidator()
    request = _request()
    frame = pd.DataFrame(
        {
            "timestamp": [
                datetime(2020, 1, 1),
                datetime(2020, 1, 1),
            ],
            "open": [1.0, 1.1],
            "high": [1.2, 1.3],
            "low": [0.9, 0.95],
            "close": [1.05, 1.15],
            "volume": [100, 200],
        }
    )
    with pytest.raises(DataValidationError):
        validator.validate(frame, request)


def test_local_csv_provider_loads_fixture() -> None:
    data_dir = Path(__file__).parents[0] / "data"
    provider = LocalCSVProvider(data_dir=data_dir)
    request = _request()
    frame = provider.fetch(request)
    assert len(frame) == 3
    assert set(frame.columns) >= {"timestamp", "open", "close"}


def test_data_manager_raises_after_all_failures(tmp_path: Path) -> None:
    cache = LocalDataCache(root=tmp_path / "cache")
    manager = DataManager(cache=cache, providers=[FailingProvider()])
    with pytest.raises(DataFetchError):
        manager.fetch(_request())


def test_data_settings_builder(tmp_path: Path) -> None:
    settings = DataSettings.defaults(cache_dir=tmp_path / "cache", data_dir=Path("tests/data"))
    manager = settings.build_manager()
    result = manager.fetch(
        DataRequest(
            symbol="AAPL",
            start=datetime(2020, 1, 1, tzinfo=timezone.utc),
            end=datetime(2020, 1, 4, tzinfo=timezone.utc),
        )
    )
    assert not result.empty
