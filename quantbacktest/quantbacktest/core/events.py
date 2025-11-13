from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Literal, Optional


class EventType(str, Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


@dataclass(slots=True)
class Event:
    event_type: EventType = field(init=False)


@dataclass(slots=True)
class MarketEvent(Event):
    symbol: str
    price: float
    timestamp: float
    metadata: Optional[Dict[str, float]] = None

    def __post_init__(self) -> None:
        self.event_type = EventType.MARKET


@dataclass(slots=True)
class SignalEvent(Event):
    symbol: str
    strength: float
    direction: Literal["LONG", "SHORT"]
    signal_id: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self) -> None:
        self.event_type = EventType.SIGNAL


@dataclass(slots=True)
class OrderEvent(Event):
    order_id: str
    symbol: str
    quantity: int
    direction: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"] = "MARKET"
    limit_price: Optional[float] = None
    signal_id: Optional[str] = None
    timestamp: Optional[float] = None
    allow_partial: bool = True

    def __post_init__(self) -> None:
        self.event_type = EventType.ORDER


@dataclass(slots=True)
class FillEvent(Event):
    order_id: str
    symbol: str
    quantity: int
    direction: Literal["BUY", "SELL"]
    fill_price: float
    commission: float = 0.0
    slippage_bps: float = 0.0
    spread_bps: float = 0.0
    timestamp: Optional[float] = None

    def __post_init__(self) -> None:
        self.event_type = EventType.FILL
