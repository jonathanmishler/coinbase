import logging
from typing import Optional, List
import math
from datetime import datetime, timedelta
import asyncio
import functools
import httpx
from .auth import Auth

def datetime_floor(x: datetime):
    return x - timedelta(seconds=x.second, microseconds=x.microsecond)


def ratelimiter(sem: asyncio.Semaphore):
    """The Semaphore should be the number rate per second you want to limit to
    For example, if the rate needs to be 10 per second, then pass Semaphore(10).
    """

    def decorator_ratelimiter(func):
        @functools.wraps(func)
        async def wrapper_ratelimiter(*args, **kwags):
            async with sem:
                value = await func(*args, **kwags)
                await asyncio.sleep(1)
            return value

        return wrapper_ratelimiter

    return decorator_ratelimiter


async def candle(
    coin_id: str,
    interval: int = 60,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[dict]:
    auth = Auth()
    base_url = "https://api.exchange.coinbase.com"
    interval_per_request = timedelta(seconds = (300 * interval))

    if end is None:
        end = datetime.now() - timedelta(seconds=60)

    if start is None:
        start = end - interval_per_request

    if start > end:
        raise ValueError("Start datetime has to be before the Date datetime")

    start = datetime_floor(start)
    end = datetime_floor(end)

    batches = math.floor((end - start) / interval_per_request)
    batch_start = end
    resutls = list()
    async with httpx.AsyncClient(base_url=base_url) as client:
        for batch in range(batches):
            batch_end = batch_start
            batch_start = batch_end - interval_per_request
            resp = await get_candle(
                client, coin_id, auth, interval, batch_start, batch_end
            )
            resutls.append(resp)
    return resutls


@ratelimiter(asyncio.Semaphore(15))
async def get_candle(
    client: httpx.Client,
    coin_id: str,
    auth: Auth,
    interval: int,
    start: datetime,
    end: datetime,
):
    endpoint = f"/products/{coin_id}/candles"
    resp = await client.get(
        url=endpoint,
        params={
            "granularity": interval,
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
        headers=auth.request_header(endpoint, "GET"),
    )

    return resp
