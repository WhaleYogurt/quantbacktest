from __future__ import annotations

import math
from typing import Iterable


def sharpe_ratio(returns: Iterable[float], risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    series = list(returns)
    if not series:
        return 0.0
    excess = [ret - risk_free / periods_per_year for ret in series]
    mean = sum(excess) / len(excess)
    variance = sum((ret - mean) ** 2 for ret in excess) / len(excess)
    std = math.sqrt(variance)
    if std == 0:
        return 0.0
    return (mean * periods_per_year) / (std * math.sqrt(periods_per_year))


def sortino_ratio(returns: Iterable[float], risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    series = list(returns)
    if not series:
        return 0.0
    excess = [ret - risk_free / periods_per_year for ret in series]
    downside = [min(0.0, ret) for ret in excess]
    downside_variance = sum(ret ** 2 for ret in downside) / len(downside)
    downside_std = math.sqrt(downside_variance)
    if downside_std == 0:
        return 0.0
    mean = sum(excess) / len(excess)
    return (mean * periods_per_year) / (downside_std * math.sqrt(periods_per_year))
