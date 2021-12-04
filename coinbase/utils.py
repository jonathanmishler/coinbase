from typing import Generator, Tuple
from datetime import datetime, timedelta


def datetime_floor(x: datetime):
    """Rounds down the datetime to the current minute"""
    return x - timedelta(seconds=x.second, microseconds=x.microsecond)


def gen_interval(
    start: datetime,
    end: datetime,
    interval: timedelta,
    offset: timedelta = timedelta(seconds=0),
    backwards: bool = False,
) -> Generator[Tuple[datetime, datetime], None, None]:
    """Generates batches of datetime intervals between 2 dates with a given timedelta,
    and checks start dates are less than end dates.  The offset is used to offset the
    next inteval start date from the last interval end date. Intervals can go back from
    the end by setting backward to true, but the tuple will be such that the first tuple
    value will be greater than the second tuple value.  The final interval will be fixed
    to the final date, so it could represent a smaller interval.
    """
    c = 1
    if start > end:
        raise ValueError("Start datetime has to be before the Date datetime")

    if backwards:
        # swap the end and start dates
        end, start = start, end
        # correct the interval and offset to go backward
        interval = -interval
        offset = -offset
        # correct the while condition
        c = -c

    # correct offset for the first interval
    interval_end = start - offset
    cond = ((end - interval_end).total_seconds() * c) > 0
    while cond:
        interval_start = interval_end + offset
        interval_end = interval_start + interval
        cond = ((end - interval_end).total_seconds() * c) > 0
        if cond:
            yield interval_start, interval_end
        else:
            yield interval_start, end
