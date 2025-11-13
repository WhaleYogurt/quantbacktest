from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence

from ..core.events import FillEvent, MarketEvent


class EngineMode(str, Enum):
    STANDARD = "standard"
    WALK_FORWARD = "walk_forward"
    GRID_SEARCH = "grid_search"


@dataclass(slots=True)
class SegmentPlan:
    segment_id: str
    events: Sequence[MarketEvent]
    parameters: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass(slots=True)
class EngineSegmentResult:
    segment_id: str
    fills: List[FillEvent]
    portfolio_snapshot: Dict[str, float]
    parameters: Optional[Dict[str, float]] = None
    duration_ms: float = 0.0

    @property
    def fill_count(self) -> int:
        return len(self.fills)


@dataclass(slots=True)
class EngineResult:
    run_id: str
    mode: EngineMode
    segments: List[EngineSegmentResult]
    metadata_path: str
    status: str = "completed"

    @property
    def fills(self) -> List[FillEvent]:
        return [fill for segment in self.segments for fill in segment.fills]
