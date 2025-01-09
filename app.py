from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import product
from typing import List, Optional

import pandas as pd
import streamlit as st
from tqdm import tqdm

from fast_flights import utils
from fast_flights.core import get_flights_from_filter
from fast_flights.filter import create_filter
from fast_flights.flights_impl import FlightData, Passengers, TFSData
from fast_flights.schema import Airport

st.set_page_config(page_title="Flights", layout="wide")
st.header("✈️ Flights Search")

if "all_flights" not in st.session_state:
    st.session_state.all_flights = []


@dataclass
class SearchParams:
    from_airports: list[Airport]
    to_airports: list[Airport]
    outbound_dates: list[datetime]
    return_dates: Optional[list[datetime]] = None
    currency: str = "EUR"
    max_stops: Optional[int] = None

    assert max_stops is None or max_stops >= 0
    assert return_dates is None or all(rd > od for od, rd in zip(outbound_dates, return_dates))  # all return dates after outbound


# functions
def run_search():
    """Run the search with the given params."""
    # single outbound date
    if len(outbound_dates) == 1:
        outbound_dates_clean = [outbound_dates[0]]
    # multiple outbound dates (range)
    else:
        outbound_dates_clean = utils.generate_date_range_between_dates(*outbound_dates)

    if return_dates:
        # single return date
        if len(return_dates) == 1:
            return_dates_clean = [return_dates[0]]
        # multiple return dates (range)
        else:
            return_dates_clean = utils.generate_date_range_between_dates(*return_dates)
    else:
        return_dates_clean = []

    search_params = SearchParams(
        from_airports=[Airport(x.split(" ")[0]) for x in from_airports],
        to_airports=[Airport(x.split(" ")[0]) for x in to_airports],
        outbound_dates=[datetime.combine(od, datetime.min.time()) for od in outbound_dates_clean],
        return_dates=[datetime.combine(rd, datetime.min.time()) for rd in return_dates_clean],
        max_stops=max_stops,
    )

    filters = create_filters_from_search_params(search_params)
    all_results = []

    for filter in tqdm(filters):
        result = get_flights_from_filter(filter, currency=search_params.currency, mode="common")
        if result:
            all_results.append(result)

    # extract flights
    all_flights = [x.flights for x in all_results]
    all_flights = [f for flights in all_flights for f in flights]  # unnest

    # store in session state
    st.session_state.all_flights = all_flights

    if not all_flights:
        st.warning("No flights found.")


def create_filters_from_search_params(search_params: SearchParams) -> List[TFSData]:
    """Create a filter object from search params."""
    all_filters = []
    combinations = list(
        product(
            search_params.from_airports,
            search_params.to_airports,
            search_params.outbound_dates,
            search_params.return_dates if search_params.return_dates else [None],
        )
    )
    for from_airport, to_airport, outbound_date, return_date in combinations:
        flight_data = [FlightData(date=outbound_date.strftime("%Y-%m-%d"), from_airport=from_airport.iata, to_airport=to_airport.iata)]
        if return_date:
            flight_data.append([FlightData(date=return_date.strftime("%Y-%m-%d"), from_airport=to_airport.iata, to_airport=from_airport.iata)])

        filter = create_filter(
            flight_data=flight_data,
            trip="round-trip" if return_date else "one-way",
            passengers=Passengers(adults=1),
            seat="economy",
            max_stops=search_params.max_stops,
        )
        all_filters.append(filter)

    return all_filters


def is_search_ready() -> bool:
    """Check if all required search params are set."""
    return all([from_airports, to_airports, outbound_dates])


# input search params
container_params = st.container(border=True)
with container_params:
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        from_airports = st.multiselect(
            "Origin airport(s)",
            options=Airport.get_all_iatas_with_names(),
            default=["FCO (Rome\u2013Fiumicino Leonardo da Vinci International Airport)"],
        )
        outbound_dates = st.date_input(
            "Outbound flight date(s)",
            value=(datetime.today() + timedelta(days=10), datetime.today() + timedelta(days=11)),
            min_value=datetime.today(),
            format="DD-MM-YYYY",
        )
    with col2:
        to_airports = st.multiselect(
            "Destination airport(s)",
            options=Airport.get_all_iatas_with_names(),
            default=["MUC (Munich Airport)", "FMM (Memmingen Allgau Airport)"],
        )
        return_dates = st.date_input(
            "Return flight date(s)",
            value=[],
            min_value=max(outbound_dates) if outbound_dates else datetime.today(),
            format="DD-MM-YYYY",
        )
    with col3:
        max_stops = st.select_slider("Max stops", options=[0, 1, 2, 3, 4, 5], value=1)

    st.button("Search", on_click=run_search, type="primary", disabled=not is_search_ready())


def make_flights_dataframe() -> pd.DataFrame:
    assert st.session_state.all_flights, "all_flights not present in session state"
    assert len(st.session_state.all_flights) > 0, "st.session_state.all_flights is an empty list"

    data = st.session_state.all_flights

    # create dataframe
    df = pd.DataFrame(data)

    # move airline_logo_url col to first position
    df = df[["airline_logo_url"] + [col for col in df.columns if col != "airline_logo_url"]]

    # make airlines a list
    df["airlines"] = df["airlines"].apply(lambda x: x.split(", ") if x else None)

    # fix data types
    df["price"] = df["price"].astype(int)

    # sort
    df = df.sort_values(["price", "stops", "duration", "departure"], ascending=True)

    return df.reset_index(drop=True)


container_results = st.container(border=False)
with container_results:
    st.write("## Results")
    if st.session_state.all_flights:
        st.info(f"{len(st.session_state.all_flights)} flights found")
        df = make_flights_dataframe()

        # format columns
        df["duration"] = df["duration"].apply(utils.format_duration_human_readable)
        df["layover_duration"] = df["layover_duration"].apply(utils.format_duration_human_readable)

        st.dataframe(
            df,
            column_config={
                "departure": st.column_config.DatetimeColumn(format="ddd D MMM, HH:mm"),
                "arrival": st.column_config.DatetimeColumn(format="ddd D MMM, HH:mm"),
                "airline_logo_url": st.column_config.ImageColumn(label="", width=None),
                "price": st.column_config.ProgressColumn(format="€%f", min_value=0, max_value=int(df.price.max())),
                # "url": st.column_config.LinkColumn(display_text="URL"),
            },
            height=600 if len(df) > 10 else None,
            use_container_width=True,
        )
        
        # stats
        st.write("### Stats")
        # TODO: create plots
