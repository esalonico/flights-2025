from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional


@dataclass
class Result:
    current_price: Literal["low", "typical", "high"]
    flights: List[Flight]


@dataclass
class Flight:
    is_best: bool
    airport_from: str
    airport_to: str
    airlines: Optional[str]
    departure: datetime
    arrival: datetime
    duration: int
    stops: int
    stops_location: Optional[str]
    layover_duration: Optional[int] | list
    delay: Optional[str]
    price: Optional[int]
    airline_logo_url: Optional[str]
    self_transfer: bool = False
    hand_luggage_only: bool = False

    @property
    def duration_human_readable(self) -> str:
        hours, minutes = divmod(self.duration, 60)
        return f"{hours} hr {minutes} min"

    @property
    def layover_duration_human_readable(self) -> Optional[str]:
        if self.layover_duration:
            hours, minutes = divmod(self.layover_duration, 60)
            return f"{hours} hr {minutes} min"
