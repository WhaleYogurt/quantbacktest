"""
Data access layer for quantbacktest.

The data package enforces cache-first retrieval, deterministic validation,
and provider fallbacks. Step 1 exposes only light scaffolding so later
milestones can plug in full-featured providers without touching callers.
"""

from .cache import LocalDataCache
from .manager import DataManager
from .settings import DataSettings, ProviderConfig
from .providers.base import DataProvider, DataRequest
from .providers.local_csv import LocalCSVProvider
from .providers.yahoo import YahooFinanceProvider
from .validator import DataValidator, DataValidationError
from .errors import DataFetchError, DataProviderError

__all__ = [
    "DataManager",
    "DataSettings",
    "ProviderConfig",
    "DataProvider",
    "DataRequest",
    "LocalDataCache",
    "LocalCSVProvider",
    "DataValidator",
    "DataValidationError",
    "DataFetchError",
    "DataProviderError",
    "YahooFinanceProvider",
]
