from __future__ import annotations

from typing import Callable, Dict, Iterable

StrategyFactory = Callable[..., object]
_REGISTRY: Dict[str, StrategyFactory] = {}


def register_strategy(name: str, factory: StrategyFactory) -> None:
    normalized = name.lower()
    _REGISTRY[normalized] = factory


def get_strategy(name: str) -> StrategyFactory:
    normalized = name.lower()
    if normalized not in _REGISTRY:
        raise KeyError(f"strategy '{name}' not registered")
    return _REGISTRY[normalized]


def available_strategies() -> Iterable[str]:
    return sorted(_REGISTRY.keys())
