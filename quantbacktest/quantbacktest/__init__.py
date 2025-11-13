"""
quantbacktest package bootstrap.

This module exposes lightweight helpers so downstream code can quickly
inspect versioning information, configure logging, and enforce deterministic
behavior. Additional subpackages (data, core, engine, etc.) are imported
lazily to keep import time low during CLI usage.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Callable

__all__ = [
    "__version__",
    "get_version",
    "load_plugin",
    "register_startup_hook",
]

__version__ = "0.2.0"
_STARTUP_HOOKS: list[Callable[[], None]] = []


def get_version() -> str:
    """Return the current package version."""
    return __version__


def register_startup_hook(callback: Callable[[], None]) -> None:
    """
    Register a callable that will be executed once when the package is imported.

    Hooks are executed in the order they are registered. They must not raise.
    """
    if not callable(callback):
        raise TypeError("callback must be callable")
    _STARTUP_HOOKS.append(callback)


def _run_startup_hooks() -> None:
    for hook in list(_STARTUP_HOOKS):
        try:
            hook()
        except Exception as exc:  # pragma: no cover - defensive guardrail
            # Importing logging lazily avoids expensive logging setup for tests.
            from .utils.logging import get_logger

            get_logger(__name__).warning("startup hook %s failed: %s", hook, exc)

    _STARTUP_HOOKS.clear()


def load_plugin(path: str) -> Any:
    """
    Dynamically import a plugin using its dotted path.

    This helper is intentionally thin so downstream users can register
    proprietary modules without modifying the core package.
    """
    module = import_module(path)
    _run_startup_hooks()
    return module


# Ensure hooks registered during import-time configuration are executed once.
_run_startup_hooks()
