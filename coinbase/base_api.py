from typing import Optional
import httpx
from .auth import CoinbaseAuth

class BaseApi:
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)
        self.auth = CoinbaseAuth()

    async def get(self, url: str, params: Optional[dict]= None) -> httpx.Response:
        return await self.client.get(url, params=params, auth=self.auth)

