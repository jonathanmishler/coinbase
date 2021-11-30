from asyncio.tasks import sleep
import logging
from os import makedirs
import re
from typing import Optional, List, Tuple, Generator
import math
from datetime import date, datetime, timedelta
import asyncio
import functools
import httpx
from .auth import CoinbaseAuth


class RateLimiter(asyncio.Semaphore):
    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(1)
        self.release()


def datetime_floor(x: datetime):
    """Rounds down the datetime to the current minute"""
    return x - timedelta(seconds=x.second, microseconds=x.microsecond)


def gen_interval(
    start: datetime,
    end: datetime,
    interval: timedelta,
    offset: timedelta = timedelta(seconds=0),
    backwards: bool = False,
) -> Generator[Tuple[datetime, datetime]]:
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


async def download(client: httpx.AsyncClient, req: httpx.Request, limiter: RateLimiter):
    async with limiter:
        resp = await client.send(req)
        resp.raise_for_status()
        return resp


class Coin:
    def __init__(self, coin_id: str) -> None:
        auth = CoinbaseAuth()
        base_url = f"https://api.exchange.coinbase.com/products/{coin_id}"
        limiter = RateLimiter(15)

    def client(self, params: Optional[dict] = None) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, auth=self.auth, params=params)

    async def history(
        self,
        resolution: int = 60,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ):
        interval_per_request = timedelta(seconds=(300 * resolution))

        if end is None:
            end = datetime.now()
        if start is None:
            start = end - interval_per_request
        start = datetime_floor(start)
        end = datetime_floor(end)
        batches = gen_interval(
            start=start,
            end=end,
            interval=interval_per_request,
            offset=timedelta(seconds=resolution),
            backwards=True,
        )
        async with self.client(params={"granularity": resolution}) as client:
            req_batches = [
                client.build_request(
                    method="GET",
                    url="/candles",
                    params={
                        "start": batch_start.isoformat(),
                        "end": batch_end.isoformat(),
                    },
                )
                for batch_end, batch_start in batches
            ]
            tasks = [self.make_request(client, req) for req in req_batches]
            resutls = await asyncio.gather(tasks)
        return resutls

    async def make_request(
        self, client: httpx.AsyncClient, req: httpx.Request
    ) -> httpx.Response:
        async with self.limiter:
            resp = await client.send(req)
            resp.raise_for_status()
            return resp