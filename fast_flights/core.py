import re
from datetime import datetime
from typing import List, Literal, Optional, Tuple

from selectolax.lexbor import LexborHTMLParser, LexborNode

from .fallback_playwright import fallback_playwright_fetch
from .filter import TFSData
from .flights_impl import FlightData, OutboundParentFlight, Passengers
from .primp import Client, Response
from .schema import Flight, Result
from .utils import convert_flight_time_str_to_datetime, get_duration_in_minutes_from_string


def fetch(params: dict) -> Response:
    client = Client(impersonate="chrome_128", verify=False)
    res = client.get("https://www.google.com/travel/flights", params=params)
    assert res.status_code == 200, f"{res.status_code} Result: {res.text_markdown}"
    print(res.url)
    return res


def get_flights_from_filter(filter: TFSData, currency: str = "EUR") -> Result:
    data = filter.as_b64()
    params = {
        "tfs": data.decode("utf-8"),
        "hl": "en",
        "tfu": "EgQIABABIgA",
        "curr": currency,
    }

    # fetch data
    try:
        res = fetch(params)
    except AssertionError as e:
        res = fallback_playwright_fetch(params)
    except Exception as e:
        raise e

    # parse data
    try:
        return parse_response(res, filter=filter)
    except Exception as e:
        raise e


def get_flights(
    *,
    flight_data: List[FlightData],
    trip: Literal["round-trip", "one-way", "multi-city"],
    passengers: Passengers,
    max_stops: Optional[int] = None,
) -> Result:
    """Get flights from the given parameters."""
    filter = TFSData.from_interface(flight_data=flight_data, trip=trip, passengers=passengers, max_stops=max_stops)
    results = get_flights_from_filter(filter=filter)

    if not results:
        return

    if not results.flights:
        return results

    # all flights for all combinations
    results_flights = [fl for fl in results.flights][0:1]
    print("Results:", len(results_flights))
    print(results_flights)

    # get return flights
    if trip == "round-trip":
        for outbound_flight in results_flights:
            subflights = []
            for subflight_idx in range(len(outbound_flight.flight_numbers)):
                subflights.append(
                    OutboundParentFlight(
                        date=outbound_flight.departure.strftime("%Y-%m-%d"),
                        from_airport=outbound_flight.airport_from,
                        to_airport=outbound_flight.airport_to,
                        airline_code=outbound_flight.flight_numbers[subflight_idx][:2],
                        flight_number=outbound_flight.flight_numbers[subflight_idx][2:],
                    )
                )

            print("SUBFLIGHTS")
            print(subflights)
            print()

            return_flights_filter = TFSData.from_interface(
                flight_data=flight_data,
                trip=trip,
                passengers=passengers,
                max_stops=max_stops,
                outbound_parent_flights=subflights,
            )

            print("FILTER")
            print(return_flights_filter.__dict__)
            x = return_flights_filter.as_b64().decode("utf-8")
            print(f"https://www.google.com/travel/flights?tfs={x}&hl=en&tfu=EgQIABABIgA&curr=EUR")
            print()

            return_flights = get_flights_from_filter(filter=return_flights_filter)

            if return_flights:
                for rf in return_flights.flights:
                    print("+++")
                    print(rf.__dict__)
                    print("+++")

    return results


def parse_response(r: Response, *, filter: TFSData, dangerously_allow_looping_last_item: bool = False) -> Result:
    class _blank:
        def text(self, *_, **__):
            return ""

        def iter(self):
            return []

    blank = _blank()

    def safe(n: Optional[LexborNode]):
        return n or blank

    def parse_airline_logo_url(item: LexborNode) -> Optional[str]:
        airline_logo_node = safe(item.css_first("div.EbY4Pc.P2UJoe"))
        airline_logo_style = airline_logo_node.attributes.get("style", "")

        pattern = r"--travel-primitives-themeable-image-default: url\((https?://[^\)]+)\);"
        match = re.search(pattern, airline_logo_style)

        if match:
            return match.group(1)

    def extract_layover_duration_from_str(s: str) -> Optional[str]:
        match = re.match(r"(?:(\d+) hr)? ?(?:(\d+) min)?", s)
        if match:
            return match.group(0)

    def extract_airline_code_and_flight_number(s: str) -> Optional[List[Tuple[str, str]]]:
        """
        Extracts the airline code and flight number from a string.

        :param s: The string to extract the airline code and flight number from.
        :return: A list of tuples containing the airline code and flight number. Returns [] if no matches are found.

        Example:
        https://www.travelimpactmodel.org/lookup/flight?itinerary=FCO-FLR-AZ-1679-20250120,FLR-MUC-EN-8191-2025012
        [("AZ", "1679"), ("EN", "8191")]

        Special cases:
        - A3 1234 (number in flight code)
        - FV 12 (flight code has only 2 digits)
        """
        pattern = r"-([A-Z0-9]{2})-(\d{2,4})-"
        result = re.findall(pattern, s)
        if not result:
            print("No airline code and flight number found in:", s)
        return result

    parser = LexborHTMLParser(r.text)
    flights = []

    for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best_flight = i == 0

        for item in fl.css("ul.Rk10dc li")[: (None if dangerously_allow_looping_last_item or i == 0 else -1)]:

            # Get airport from & to
            airports = item.css("div.QylvBf span span")
            if airports:
                airports = [a for a in airports if a.attributes.get("jscontroller") == "cNtv4b"]
                assert len(airports) == 2, "Invalid airport nodes"
                airport_from = airports[0].text(strip=True)
                airport_to = airports[1].text(strip=True)
            else:
                airport_from = airport_to = None

            # (flight name)
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf")).text(strip=True)

            # Get arrival time ahead (delta days)
            time_ahead = safe(item.css_first("span.bOzv6")).text().strip()
            try:
                time_ahead = int(time_ahead)
            except ValueError:
                time_ahead = None

            # Get departure & arrival time
            dp_ar_node = item.css("span.mv1WYe div")
            search_date = datetime.strptime(filter.flight_data[0].date, "%Y-%m-%d")
            try:
                departure_str = dp_ar_node[0].text(strip=True)
                departure = convert_flight_time_str_to_datetime(search_date=search_date, datetime_str=departure_str)

                arrival_str = dp_ar_node[1].text(strip=True)
                arrival = convert_flight_time_str_to_datetime(search_date=search_date, datetime_str=arrival_str, delta_days=time_ahead)
            except Exception as e:
                print("Error parsing departure and arrival time:", e)
                print(dp_ar_node)
                print(dp_ar_node[0].text(strip=True))
                print(dp_ar_node[1].text(strip=True))

            # Get airlines
            airlines = name.split(".")[-1].strip() if name else None
            if airlines:
                airlines = airlines.split("Operated by")[0].strip()

            # Get flight number
            flight_info_raw = item.css_first(".NZRfve")
            flight_info_raw = flight_info_raw.attributes.get("data-travelimpactmodelwebsiteurl")
            flight_info = extract_airline_code_and_flight_number(flight_info_raw)
            if flight_info:
                flight_numbers = [f"{code}{number}" for code, number in flight_info]
            else:
                flight_numbers = None

            # Get duration
            duration_str = safe(item.css_first("li div.Ak5kof div")).text()
            duration = get_duration_in_minutes_from_string(duration_str)

            # Get flight stops
            stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()
            stops = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])

            # Get stops location
            stops_location = item.css(".BbR8Ec div.sSHqwe.tPgKwe.ogfYpf span")
            if stops_location:
                stops_location = [x.text(strip=True) for x in stops_location if x.attributes.get("jscontroller") == "cNtv4b"]
            stops_location = stops_location or None

            # Get layover duration
            layover_duration_str = safe(item.css_first(".BbR8Ec div.sSHqwe.tPgKwe.ogfYpf")).text(strip=True)
            layover_duration_str = extract_layover_duration_from_str(layover_duration_str)

            if layover_duration_str and len(layover_duration_str) > 1:
                layover_duration = get_duration_in_minutes_from_string(layover_duration_str)
            else:
                layover_duration = None

            # Get delay
            delay = safe(item.css_first(".GsCCve")).text() or None

            # Get prices
            price = item.css_first(".YMlIz.FpEdX").text(strip=True) or None
            price = price.replace(",", "") if price else None
            if price and price != "Price unavailable":
                price = int(re.search(r"(\d+)", price).group(1)) if price else None  # convert to int

            # Get airline logo url
            airline_logo_url = parse_airline_logo_url(item)

            # Get self transfer
            self_transfer = "Self transfer" in name

            # Get hand luggage only
            hand_luggage_only = item.css_matches("svg.vmWDCc")

            flights.append(
                {
                    "is_best": is_best_flight,
                    "airport_from": airport_from,
                    "airport_to": airport_to,
                    "airlines": airlines,
                    "flight_numbers": flight_numbers,
                    "departure": departure,
                    "arrival": arrival,
                    "duration": duration,
                    "stops": stops,
                    "stops_location": stops_location,
                    "layover_duration": layover_duration,
                    "delay": delay,
                    "price": price,
                    "airline_logo_url": airline_logo_url,
                    "self_transfer": self_transfer,
                    "hand_luggage_only": hand_luggage_only,
                }
            )

    current_price = safe(parser.css_first("span.gOatQ")).text()

    if not flights:
        print("No flights found")
        return

    # Remove duplicates
    unique_flights = []
    for fl in flights:
        flight_obj = Flight(**fl)
        if flight_obj not in unique_flights:
            unique_flights.append(flight_obj)

    flight_objects = unique_flights

    return Result(current_price=current_price, flights=flight_objects)  # type: ignore
