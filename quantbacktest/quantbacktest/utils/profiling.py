from __future__ import annotations

import cProfile
import pstats
from pathlib import Path
from typing import Any, Callable, Dict, Tuple


def profile_callable(func: Callable[..., Any], *args: Any, output: Path, **kwargs: Any) -> Tuple[Any, Dict[str, float]]:
    """
    Profile `func` and write human-readable stats to `output`.

    Returns the function result and a dictionary containing summary metrics
    (total time and primitive call count) so callers can fold the data into
    higher-level reports.
    """

    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        stats = pstats.Stats(profiler, stream=handle)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats(40)

    stats_payload = profiler.getstats()
    total_time = sum(stat.totaltime for stat in stats_payload) if stats_payload else 0.0
    return result, {"total_time": total_time}
