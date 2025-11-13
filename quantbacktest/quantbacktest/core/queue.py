from __future__ import annotations

from collections import deque
from typing import Deque, Iterator, Optional

from .events import Event


class EventQueue:
    """Thread-safe ready queue used by the engine."""

    def __init__(self) -> None:
        self._queue: Deque[Event] = deque()

    def put(self, event: Event) -> None:
        self._queue.append(event)

    def get(self) -> Optional[Event]:
        if not self._queue:
            return None
        return self._queue.popleft()

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._queue)

    def __iter__(self) -> Iterator[Event]:
        while self._queue:
            yield self._queue.popleft()
