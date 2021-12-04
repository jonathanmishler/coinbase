import logging
from os import makedirs
from typing import Optional, List, Tuple, Generator
from datetime import datetime, timedelta
import httpx
import psycopg
from .auth import CoinbaseAuth
import utils
from db.models import CoinHistory
from db.settings import Settings


class Coin:
    def __init__(self, coin_id: str) -> None:
        self.auth = CoinbaseAuth()
        self.coin_id = coin_id
        self.base_url = f"https://api.exchange.coinbase.com/products/{self.coin_id}"
        self.db_settings = Settings()
        # limiter = RateLimiter(15)

    def client(self, params: Optional[dict] = None) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, auth=self.auth, params=params)

    def history(
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
        start = utils.datetime_floor(start)
        end = utils.datetime_floor(end)
        batches = utils.gen_interval(
            start=start,
            end=end,
            interval=interval_per_request,
            offset=timedelta(seconds=resolution),
            backwards=True,
        )
        with self.client(params={"granularity": resolution}) as client, psycopg.connect(
            self.db_settings.conn_str
        ) as conn:
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
            results = [
                self.write_to_table(self.make_request(client, req), conn)
                for req in req_batches
            ]
        return results

    def make_request(
        self, client: httpx.AsyncClient, req: httpx.Request
    ) -> httpx.Response:
        # async with self.limiter:
        resp = client.send(req)
        resp.raise_for_status()
        return resp

    def write_to_table(self, resp, conn):
        with conn.cursor() as cur:
            coin_history = CoinHistory.from_coinbase(resp.text)
            cur.executemany(
                CoinHistory.insert_str(self.coin_id), [row.as_tuple() for row in coin_history]
            )
        conn.commit()
