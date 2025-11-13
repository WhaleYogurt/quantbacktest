from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

from .cache import LocalDataCache
from .manager import DataManager
from .providers.local_csv import LocalCSVProvider
from .providers.yahoo import YahooFinanceProvider
from .validator import DataValidator


@dataclass(slots=True)
class ProviderConfig:
    name: str
    params: dict = field(default_factory=dict)


@dataclass(slots=True)
class DataSettings:
    cache_dir: Path
    provider_chain: Sequence[ProviderConfig]
    data_dir: Path | None = None

    @classmethod
    def defaults(cls, cache_dir: Path, data_dir: Path | None = None) -> "DataSettings":
        return cls(
            cache_dir=cache_dir,
            data_dir=data_dir,
            provider_chain=[
                ProviderConfig(name="local_csv"),
                ProviderConfig(name="yahoo", params={"retries": 3, "backoff": 1.0}),
            ],
        )

    def build_manager(self) -> DataManager:
        cache = LocalDataCache(root=self.cache_dir)
        providers = []
        for config in self.provider_chain:
            if config.name == "local_csv":
                if not self.data_dir:
                    continue
                providers.append(LocalCSVProvider(data_dir=self.data_dir, **config.params))
            elif config.name == "yahoo":
                providers.append(YahooFinanceProvider(**config.params))
            else:
                raise ValueError(f"Unknown provider '{config.name}'")
        if not providers:
            raise ValueError("No providers configured for DataSettings")
        return DataManager(cache=cache, providers=providers, validator=DataValidator())
