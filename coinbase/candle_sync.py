import logging
from typing import Optional, List, Tuple
import math
from datetime import date, datetime, timedelta
import asyncio
import functools
import httpx
from .auth import CoinbaseAuth


def datetime_floor(x: datetime):
    return x - timedelta(seconds=x.second, microseconds=x.microsecond)


def generate_interval(
    start: datetime,
    end: datetime,
    interval: timedelta,
    offset: timedelta = timedelta(seconds=0),
    backwards: bool = False,
) -> Tuple[datetime, datetime]:
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


def candle(
    coin_id: str,
    resolution: int = 60,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[dict]:

    auth = CoinbaseAuth()
    base_url = "https://api.exchange.coinbase.com/products"
    interval_per_request = timedelta(seconds=(300 * resolution))

    if end is None:
        end = datetime.now()

    if start is None:
        start = end - interval_per_request

    start = datetime_floor(start)
    end = datetime_floor(end)

    batches = generate_interval(
        start=start,
        end=end,
        interval=interval_per_request,
        offset=timedelta(seconds=60),
        backwards=True,
    )
    resutls = list()
    with httpx.Client(base_url=base_url, auth=auth) as client:
        for batch_end, batch_start in batches:
            resp = client.get(
                url=f"/{coin_id}/candles",
                params={
                    "granularity": resolution,
                    "start": batch_start.isoformat(),
                    "end": batch_end.isoformat(),
                },
            )
            resp.raise_for_status()
            resutls.append(resp)
    return resutls
