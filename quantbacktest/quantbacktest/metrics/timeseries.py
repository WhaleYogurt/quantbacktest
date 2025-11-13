from __future__ import annotations

from typing import Iterable, List


def to_cumulative_returns(returns: Iterable[float]) -> List[float]:
    cumulative = []
    prod = 1.0
    for ret in returns:
        prod *= 1.0 + ret
        cumulative.append(prod - 1.0)
    return cumulative


def rolling_max(values: Iterable[float]) -> List[float]:
    max_so_far = float("-inf")
    results: List[float] = []
    for value in values:
        max_so_far = max(max_so_far, value)
        results.append(max_so_far)
    return results


def max_drawdown(returns: Iterable[float]) -> float:
    cumulative = to_cumulative_returns(returns)
    peak = rolling_max(cumulative)
    drawdowns = [cum - pk for cum, pk in zip(cumulative, peak)]
    return abs(min(drawdowns, default=0.0))


def annualized_return(avg_return: float, periods_per_year: int = 252) -> float:
    base = 1.0 + avg_return
    if base <= 0:
        return -1.0
    try:
        return base ** periods_per_year - 1.0
    except OverflowError:
        return float("inf")
