from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from typing import Iterable, List

import pandas as pd

from ..utils.logging import get_logger
from .cache import LocalDataCache
from .errors import DataFetchError, DataProviderError, DataValidationError
from .providers.base import DataProvider, DataRequest
from .validator import DataValidator


@dataclass(slots=True)
class DataManager:
    cache: LocalDataCache
    providers: Iterable[DataProvider]
    validator: DataValidator = field(default_factory=DataValidator)
    _providers: List[DataProvider] = field(init=False, repr=False)
    logger: Logger = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_providers", list(self.providers))
        if not self._providers:
            raise ValueError("at least one provider must be configured")
        object.__setattr__(self, "logger", get_logger(self.__class__.__name__))

    def fetch(self, request: DataRequest) -> pd.DataFrame:
        cache_key = request.cache_key()
        cached = self.cache.load_frame(cache_key)
        if cached is not None:
            self.logger.debug("cache hit for %s", cache_key)
            return self.validator.validate(cached, request)

        failures: List[str] = []
        for provider in self._providers:
            try:
                raw_frame = provider.fetch(request)
                validated = self.validator.validate(raw_frame, request)
                self.cache.store_frame(cache_key, validated)
                self.logger.info("fetched %s rows from %s", len(validated), provider.name)
                return validated
            except (DataProviderError, DataValidationError) as exc:
                failures.append(f"{provider.name}: {exc}")
                self.logger.warning("provider %s failed: %s", provider.name, exc)

        raise DataFetchError(message="All providers failed", causes=failures)
