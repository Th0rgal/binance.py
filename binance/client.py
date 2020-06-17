import logging
import aiohttp
from .http import HttpClient


class Client:
    def __init__(self, endpoint="https://api.binance.com"):
        self.http = HttpClient("https://api.binance.com")

    def connect(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        return self

    async def load(self):
        infos = await self.http.fetch_exchange_info()
        self.rate_limits = infos["rateLimits"]
        return self
