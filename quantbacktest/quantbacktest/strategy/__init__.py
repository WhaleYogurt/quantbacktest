"""Strategy interfaces, helpers, and registry."""

from .base import BaseStrategy, Strategy, StaticSignalStrategy
from .context import StrategyContext
from .indicators import IndicatorCache
from .mean_reversion import MeanReversionStrategy
from .momentum import AAPLMomentumStrategy
from .registry import available_strategies, get_strategy, register_strategy

__all__ = [
    "Strategy",
    "BaseStrategy",
    "StaticSignalStrategy",
    "StrategyContext",
    "IndicatorCache",
    "AAPLMomentumStrategy",
    "MeanReversionStrategy",
    "register_strategy",
    "get_strategy",
    "available_strategies",
]


register_strategy("static", StaticSignalStrategy)
register_strategy("momentum", AAPLMomentumStrategy)
register_strategy("mean_reversion", MeanReversionStrategy)
