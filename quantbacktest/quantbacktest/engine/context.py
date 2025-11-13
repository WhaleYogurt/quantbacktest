from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..portfolio import PortfolioState
from ..utils.random import DeterministicRandom


@dataclass(slots=True)
class EngineContext:
    """
    Shared context object used during backtests.

    The context exposes deterministic random sources, references to the
    portfolio, scratch storage, and filesystem paths for caching/results.
    """

    portfolio: PortfolioState
    run_id: str
    output_dir: Path
    randomizer: DeterministicRandom

    def ensure_output_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir
