from asyncio.locks import Semaphore
from asyncio.tasks import sleep
import logging
import time
from typing import Optional, List, Tuple, Generator
import math
from datetime import datetime, timedelta
import asyncio
import httpx
from .auth import CoinbaseAuth
import utils


class Coin:
    def __init__(self, coin_id: str) -> None:
        self.auth = CoinbaseAuth()
        self.base_url = f"https://api.exchange.coinbase.com/products/{coin_id}"

    def client(self, params: Optional[dict] = None) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, auth=self.auth, params=params)

    async def history(
        self,
        resolution: int = 60,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ):
        interval_per_request = timedelta(seconds=(300 * resolution))
        self.limiter = Semaphore(10)

        if end is None:
            end = datetime.now()
        if start is None:
            start = end - interval_per_request
        start = utils.datetime_floor(start)
        end = utils.datetime_floor(end)
        batches = utils.gen_interval(
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
            results = await asyncio.gather(*tasks)
        return results

    async def make_request(
        self, client: httpx.AsyncClient, req: httpx.Request
    ) -> httpx.Response:
        async with self.limiter:
            logging.info("Making Request")
            resp = await client.send(req)
            resp.raise_for_status()
            await asyncio.sleep(1)
            return resp
