from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from ..core.events import MarketEvent
from .modes import EngineMode, SegmentPlan


class RunScheduler:
    """
    Produces deterministic segment plans for the engine.
    """

    def __init__(
        self,
        mode: EngineMode,
        walk_forward_window: int = 0,
        grid_parameters: Sequence[Dict[str, float]] | None = None,
    ) -> None:
        self.mode = mode
        self.walk_forward_window = max(0, walk_forward_window)
        self.grid_parameters = list(grid_parameters or [{}])

    def plan(self, market_events: Iterable[MarketEvent]) -> List[SegmentPlan]:
        events = list(market_events)
        if not events:
            return []

        if self.mode == EngineMode.WALK_FORWARD:
            return self._plan_walk_forward(events)
        if self.mode == EngineMode.GRID_SEARCH:
            return self._plan_grid_search(events)
        return [SegmentPlan(segment_id="segment-1", events=events)]

    def _plan_walk_forward(self, events: List[MarketEvent]) -> List[SegmentPlan]:
        window = self.walk_forward_window or max(1, len(events) // 5)
        segments: List[SegmentPlan] = []
        idx = 0
        segment_idx = 1
        while idx < len(events):
            chunk = events[idx : idx + window]
            metadata = {
                "window_start_index": str(idx),
                "window_end_index": str(idx + len(chunk) - 1),
            }
            segments.append(SegmentPlan(segment_id=f"wf-{segment_idx}", events=chunk, metadata=metadata))
            idx += window
            segment_idx += 1
        return segments

    def _plan_grid_search(self, events: List[MarketEvent]) -> List[SegmentPlan]:
        segments: List[SegmentPlan] = []
        for idx, params in enumerate(self.grid_parameters, 1):
            metadata = {"grid_index": str(idx)}
            segments.append(
                SegmentPlan(
                    segment_id=f"grid-{idx}",
                    events=events,
                    parameters=params,
                    metadata=metadata,
                )
            )
        return segments
