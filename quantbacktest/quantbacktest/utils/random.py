from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence, TypeVar

T = TypeVar("T")


def set_global_seed(seed: int) -> None:
    random.seed(seed)


@dataclass
class DeterministicRandom:
    seed: int

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def randint(self, low: int, high: int) -> int:
        return self._rng.randint(low, high)

    def choice(self, items: Sequence[T]) -> T:
        return self._rng.choice(items)
