from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ..portfolio import PortfolioState
from .indicators import IndicatorCache


@dataclass(slots=True)
class StrategyContext:
    """
    Read-only view into portfolio state, indicator cache, and metadata.
    """

    name: str
    portfolio: PortfolioState
    indicator_cache: IndicatorCache
    random_seed: int
    metadata: Optional[Dict[str, str]] = None

    def snapshot(self) -> Dict[str, float]:
        return self.portfolio.snapshot()
