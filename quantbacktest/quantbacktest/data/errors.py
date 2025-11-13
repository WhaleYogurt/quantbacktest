from __future__ import annotations

from dataclasses import dataclass
from typing import List


class DataProviderError(RuntimeError):
    """Raised when a provider cannot fulfill a request."""


@dataclass(slots=True)
class DataFetchError(RuntimeError):
    message: str
    causes: List[str]

    def __str__(self) -> str:
        joined = "; ".join(self.causes)
        return f"{self.message}: {joined}"


class DataValidationError(RuntimeError):
    """Raised when retrieved data violates validation rules."""
