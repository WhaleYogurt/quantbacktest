from __future__ import annotations

import pytest

from quantbacktest.strategy import StaticSignalStrategy, available_strategies, get_strategy, register_strategy


def test_registry_lifecycle() -> None:
    register_strategy("custom", StaticSignalStrategy)
    factory = get_strategy("custom")
    assert isinstance(factory(), StaticSignalStrategy)
    assert "custom" in available_strategies()


def test_get_strategy_raises_for_missing() -> None:
    with pytest.raises(KeyError):
        get_strategy("missing-strategy")
