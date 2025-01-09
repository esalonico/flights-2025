from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional

DATA_FOLDER = "data"


@dataclass
class Result:
    current_price: Literal["low", "typical", "high"]
    flights: List[Flight]


with open(f"{DATA_FOLDER}/airports.json", "r") as f:
    AIRPORTS_DATA = json.load(f)


@dataclass
class Airport:
    iata: str
    icao_code: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    continent: Optional[str] = None
    iso_country: Optional[str] = None
    iso_region: Optional[str] = None
    municipality: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    def __init__(self, iata: str):
        if iata not in AIRPORTS_DATA:
            raise ValueError(f"No data available for IATA code '{iata}'")

        airport_data = AIRPORTS_DATA[iata]
        # set iata code
        self.iata = iata
        
        # set other attributes
        for key, value in airport_data.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return self.iata

    @classmethod
    def get_all_iatas(self) -> List[str]:
        return list(AIRPORTS_DATA.keys())

    @classmethod
    def get_all_iatas_with_names(self) -> List[str]:
        return [f"{k} ({v['name']})" for k, v in AIRPORTS_DATA.items()]


Airport("FCO")


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

    # allow comparison of Flight objects
    def __eq__(self, other: Flight) -> bool:
        conditions = [
            self.airport_from == other.airport_from,
            self.airport_to == other.airport_to,
            self.departure == other.departure,
            self.arrival == other.arrival,
            self.price == other.price,
            self.airlines == other.airlines,
        ]

        return all(conditions)
