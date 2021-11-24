from .base_api import BaseApi

class Market(BaseApi):

    async def coins(self):
        return await self.get("/products")