from __future__ import annotations

import logging
from logging import Logger
from typing import Optional

_LOGGING_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> Logger:
    configure_logging()
    return logging.getLogger(name if name else "quantbacktest")
