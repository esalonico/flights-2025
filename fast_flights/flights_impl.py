import base64
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Literal, Optional

from . import flights_pb2 as PB  # protobuf generated code

if TYPE_CHECKING:
    PB: Any


class OutboundParentFlight:
    """Represents the outbound parent flight data when searching for return flights."""

    __slots__ = ("date", "from_airport", "to_airport", "airline_code", "flight_number")
    date: str
    from_airport: str
    to_airport: str
    airline_code: str
    flight_number: str

    def __init__(self, *, date: str, from_airport: str, to_airport: str, airline_code: str, flight_number: str):
        assert datetime.strptime(date, "%Y-%m-%d"), "Invalid date format. Use YYYY-MM-DD"

        self.date = date
        self.from_airport = from_airport
        self.to_airport = to_airport
        self.airline_code = airline_code
        self.flight_number = flight_number

    def attach(self, flight_data: PB.FlightData):  # type: ignore
        """
        Attach outbound parent flight data (self) to the provided protobuf object.

        :param flight_data: The protobuf FlightData object to which the outbound parent flight data will be attached.
        """
        for f in flight_data:
            outbound_flight = f.outbound_flight.add()
            outbound_flight.from_airport = self.from_airport
            outbound_flight.date = self.date
            outbound_flight.to_airport = self.to_airport
            outbound_flight.airline_code = self.airline_code
            outbound_flight.flight_number = self.flight_number

    def __repr__(self):
        return f"OutboundParentFlight(date={self.date!r}, from_airport={self.from_airport!r}, to_airport={self.to_airport!r}, airline_code={self.airline_code!r}, flight_number={self.flight_number!r})"


class FlightData:
    """Represents flight data."""

    __slots__ = ("date", "from_airport", "to_airport", "max_stops", "outbound_flight")
    date: str
    from_airport: str
    to_airport: str
    max_stops: Optional[int]
    outbound_flight: Optional[OutboundParentFlight]

    def __init__(
        self,
        *,
        date: str,
        from_airport: str,
        to_airport: str,
        max_stops: Optional[int] = None,
        outbound_flight: Optional[OutboundParentFlight] = None,
    ):
        assert datetime.strptime(date, "%Y-%m-%d"), "Invalid date format. Use YYYY-MM-DD"
        assert datetime.strptime(date, "%Y-%m-%d") >= datetime.now(), "Date must be in the future"
        assert isinstance(from_airport, str) and isinstance(to_airport, str), "Airport codes must be strings"

        self.date = date
        self.from_airport = from_airport
        self.to_airport = to_airport
        self.max_stops = max_stops
        self.outbound_flight = outbound_flight

    def attach(self, info: PB.Info):  # type: ignore
        """
        Attach flight data (self) to the provided protobuf object.

        info (PB.Info): The protobuf Info object to which the flight data will be attached.
        """
        data = info.data.add()

        data.date = self.date
        data.from_flight.airport = self.from_airport
        data.to_flight.airport = self.to_airport

        if self.max_stops is not None:
            data.max_stops = self.max_stops

    def __repr__(self) -> str:
        return f"FlightData(date={self.date!r}, from_airport={self.from_airport!r}, to_airport={self.to_airport!r}, max_stops={self.max_stops!r})"


class Passengers:
    def __init__(self, n: int = 1):
        assert n <= 9, "Too many passengers (> 9)"

        self.pb = [PB.Passenger.ADULT for _ in range(n)]

        self._data = n

    def attach(self, info: PB.Info):  # type: ignore
        """
        Attach passenger data information to the provided protobuf object.

        :param info: The protobuf Info object to which the passenger data will be attached.
        """
        for p in self.pb:
            info.passengers.append(p)

    def __repr__(self) -> str:
        return f"Passengers({self._data})"


class TFSData:
    """
    For internal use only.

    For External use, use TFSData.from_interface() instead.
    """

    def __init__(
        self,
        *,
        flight_data: List[FlightData],
        trip: PB.Trip,  # type: ignore
        passengers: Passengers,
        max_stops: Optional[int] = None,
        outbound_parent_flights: Optional[List[OutboundParentFlight]] = None,  # type: ignore
    ):
        self.flight_data = flight_data
        self.seat = PB.Seat.ECONOMY  # default to economy
        self.trip = trip
        self.passengers = passengers
        self.max_stops = max_stops
        self.outbound_parent_flights = outbound_parent_flights

    def pb(self) -> PB.Info:  # type: ignore
        """
        Convert the TFSData instance to a PB.Info protobuf object.

        :return PB.Info: The protobuf Info object representing the TFSData.
        """
        info = PB.Info()

        info.seat = self.seat
        info.trip = self.trip

        # addach passenger data to the protobuf object
        self.passengers.attach(info)

        # attach each flight data entry to the protobuf object
        for fd in self.flight_data:
            fd.attach(info)

        # # if outbound_parent_flight is set, attach it to the protobuf object
        # if self.outbound_parent_flights is not None:
        #     for parent_flight in self.outbound_parent_flights:
        #         parent_flight.attach(info.data)

        # if max_stops is set, attach it to all flight data entries
        if self.max_stops is not None:
            for flight in info.data:
                flight.max_stops = self.max_stops

        return info

    def to_string(self) -> bytes:
        return self.pb().SerializeToString()

    def as_b64(self) -> bytes:
        return base64.b64encode(self.to_string())

    @staticmethod
    def from_interface(
        *,
        flight_data: List[FlightData],
        trip: Literal["round-trip", "one-way", "multi-city"],
        passengers: Passengers,
        max_stops: Optional[int] = None,
        outbound_parent_flights: Optional[List[OutboundParentFlight]] = None,
    ):
        """Use '?tfs=' from an interface."""

        # convert the input data to the protobuf format
        trip_t = {
            "round-trip": PB.Trip.ROUND_TRIP,
            "one-way": PB.Trip.ONE_WAY,
            "multi-city": PB.Trip.MULTI_CITY,
        }[trip]

        # return the TFSData object
        return TFSData(
            flight_data=flight_data,
            trip=trip_t,
            passengers=passengers,
            max_stops=max_stops,
            outbound_parent_flights=outbound_parent_flights,
        )
