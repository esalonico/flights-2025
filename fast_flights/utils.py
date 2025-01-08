import re
from datetime import datetime, timedelta


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
    assert bool(re.search("hr|min", str(s))), "Invalid duration string format"

    match = re.match(r"(?:(\d+) hr)? ?(?:(\d+) min)?", s)
    h, m = match.groups(default="0")
    return int(h) * 60 + int(m)
