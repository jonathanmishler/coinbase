from typing import Optional
import httpx
from .auth import Auth

class BaseApi:
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)
        self.auth = Auth()

    async def request(self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None) -> httpx.Response:
        req = await self.client.request(
            method = method.upper(),
            url = endpoint,
            headers = self.auth.request_header(endpoint, method, data),
            params=params,
            data=data
        )
        return req

    async def get(self, url: str, params: Optional[dict]= None) -> httpx.Response:
        return await self.request("GET", url, params=params)

