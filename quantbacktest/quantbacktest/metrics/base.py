from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .timeseries import annualized_return, max_drawdown, to_cumulative_returns


@dataclass(slots=True)
class PerformanceReport:
    returns: Sequence[float]
    cumulative_return: float
    average_return: float
    annualized_return: float
    max_drawdown: float


def compute_basic_metrics(returns: Iterable[float]) -> PerformanceReport:
    normalized = list(returns)
    cumulative_curve = to_cumulative_returns(normalized)
    cumulative = cumulative_curve[-1] if cumulative_curve else 0.0
    avg = sum(normalized) / len(normalized) if normalized else 0.0
    return PerformanceReport(
        returns=normalized,
        cumulative_return=cumulative,
        average_return=avg,
        annualized_return=annualized_return(avg),
        max_drawdown=max_drawdown(normalized),
    )
