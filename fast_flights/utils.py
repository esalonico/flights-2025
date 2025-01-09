import re
from datetime import date, datetime, timedelta
from typing import List, Optional

import numpy as np


def convert_flight_time_str_to_datetime(search_date: datetime, datetime_str: str, delta_days: int = 0) -> datetime:
    """
    Convert flight time string as shown in Google Flights to datetime object.

    Google's datetime format example:
    - 7:05 PM on Tue, Apr 1
    - 6:25 AM on Mon, Mar 31

    :param search_date: Date for which you are searching the flight
    :param datetime_str: Flight time string
    :param delta_days: Number of days to add/subtract to the datetime object (for arrival time)
    :return: Flight time as datetime object
    """
    # Google Flights datetime format
    format = "%I:%M %p on %a, %b %d %Y"

    # add year to the datetime string
    datetime_str += f" {search_date.year}"

    try:
        datetime_obj = datetime.strptime(datetime_str, format)
        if delta_days:
            datetime_obj += timedelta(days=delta_days)

        return datetime_obj

    except Exception as e:
        raise ValueError(f"Invalid datetime format: {datetime_str}") from e


def get_duration_in_minutes_from_string(s: str) -> int:
    """
    Returns the duration in minutes from a string.

    :param s: Duration string in the format "X hr Y min" or "X min".
    :return: Duration in minutes.

    Examples:
        3 hr 20 min --> 60*3 + 20 = 200
        20 min --> 20
        5 hr 55 min --> 60*5 + 55 = 355
    """
    assert bool(re.search("hr|min", str(s))), "Invalid duration string format: %s" % s

    match = re.match(r"(?:(\d+) hr)? ?(?:(\d+) min)?", s)
    h, m = match.groups(default="0")
    return int(h) * 60 + int(m)


def format_duration_human_readable(input_mins: Optional[int]) -> Optional[str]:
    """
    Format duration in minutes to human-readable format.
    :param input_mins: duration in minutes.

    :return: Human-readable duration e.g. "2 hr 30 min". Returns None if input is None.
    """
    if not input_mins or np.isnan(input_mins):
        return None

    hours = int(input_mins // 60)
    mins = int(input_mins % 60)

    if hours > 0:
        return f"{hours} hr {mins} min" if mins > 0 else f"{hours} hr"
    else:
        return f"{mins} min"


def generate_date_range_between_dates(start_date: date, end_date: date) -> List[date]:
    """
    Generate a list of dates between two dates

    :param start_date: the start date
    :param end_date: the end date
    :return: a list of dates between the two dates
    """
    assert start_date <= end_date, "Start date must be before or equal to end date"

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list
