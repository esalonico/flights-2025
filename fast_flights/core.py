import re
from typing import List, Literal, Optional

from selectolax.lexbor import LexborHTMLParser, LexborNode

from .fallback_playwright import fallback_playwright_fetch
from .filter import TFSData
from .flights_impl import FlightData, Passengers
from .primp import Client, Response
from .schema import Flight, Result


def fetch(params: dict) -> Response:
    client = Client(impersonate="chrome_128", verify=False)
    res = client.get("https://www.google.com/travel/flights", params=params)
    print(res.url)
    assert res.status_code == 200, f"{res.status_code} Result: {res.text_markdown}"
    return res


def get_flights_from_filter(
    filter: TFSData,
    currency: str = "",
    *,
    mode: Literal["common", "fallback", "force-fallback"] = "common",
) -> Result:
    data = filter.as_b64()

    params = {
        "tfs": data.decode("utf-8"),
        "hl": "en",
        "tfu": "EgQIABABIgA",
        "curr": currency,
    }

    if mode in {"common", "fallback"}:
        try:
            res = fetch(params)
        except AssertionError as e:
            if mode == "fallback":
                res = fallback_playwright_fetch(params)
            else:
                raise e

    else:
        res = fallback_playwright_fetch(params)

    try:
        return parse_response(res)
    except RuntimeError as e:
        if mode == "fallback":
            return get_flights_from_filter(filter, mode="force-fallback")
        raise e


def get_flights(
    *,
    flight_data: List[FlightData],
    trip: Literal["round-trip", "one-way", "multi-city"],
    passengers: Passengers,
    seat: Literal["economy", "premium-economy", "business", "first"],
    fetch_mode: Literal["common", "fallback", "force-fallback"] = "common",
    max_stops: Optional[int] = None,
) -> Result:
    return get_flights_from_filter(
        TFSData.from_interface(
            flight_data=flight_data,
            trip=trip,
            passengers=passengers,
            seat=seat,
            max_stops=max_stops,
        ),
        mode=fetch_mode,
    )


def parse_response(r: Response, *, dangerously_allow_looping_last_item: bool = False) -> Result:
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

    parser = LexborHTMLParser(r.text)
    flights = []

    for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best_flight = i == 0

        for item in fl.css("ul.Rk10dc li")[: (None if dangerously_allow_looping_last_item or i == 0 else -1)]:
            # Flight name
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf")).text(strip=True)

            # Get departure & arrival time
            dp_ar_node = item.css("span.mv1WYe div")
            try:
                departure_time = dp_ar_node[0].text(strip=True)
                arrival_time = dp_ar_node[1].text(strip=True)
            except IndexError:
                # sometimes this is not present
                departure_time = ""
                arrival_time = ""

            # Get arrival time ahead
            time_ahead = safe(item.css_first("span.bOzv6")).text()

            # Get duration
            duration = safe(item.css_first("li div.Ak5kof div")).text()

            # Get flight stops
            stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()

            # Get delay
            delay = safe(item.css_first(".GsCCve")).text() or None

            # Get prices
            price = safe(item.css_first(".YMlIz.FpEdX")).text() or "0"

            # Get airline logo url
            airline_logo_url = parse_airline_logo_url(item)

            # Get self transfer
            self_transfer = "Self transfer" in name

            # Get hand luggage only
            hand_luggage_only = item.css_matches("svg.vmWDCc")

            # Stops formatting
            try:
                stops_fmt = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])
            except ValueError:
                stops_fmt = "Unknown"

            flights.append(
                {
                    "is_best": is_best_flight,
                    "name": name,
                    "departure": " ".join(departure_time.split()),
                    "arrival": " ".join(arrival_time.split()),
                    "arrival_time_ahead": time_ahead,
                    "duration": duration,
                    "stops": stops_fmt,
                    "delay": delay,
                    "price": price.replace(",", ""),
                    "airline_logo_url": airline_logo_url,
                    "self_transfer": self_transfer,
                    "hand_luggage_only": hand_luggage_only,
                }
            )

    current_price = safe(parser.css_first("span.gOatQ")).text()
    if not flights:
        raise RuntimeError("No flights found:\n{}".format(r.text_markdown))

    return Result(current_price=current_price, flights=[Flight(**fl) for fl in flights])  # type: ignore
