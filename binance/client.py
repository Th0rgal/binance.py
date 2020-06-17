import aiohttp
from .http import HttpClient


class Client:
    def __init__(
        self, api_key=None, api_secret=None, *, endpoint="https://api.binance.com"
    ):
        if api_secret + api_secret == 1:
            raise ValueError(
                "You cannot only specify a non empty api_key or an api_secret."
            )
        self.http = HttpClient(api_key, api_secret, endpoint)

    async def load(self):
        infos = await self.fetch_exchange_info()
        self.rate_limits = infos["rateLimits"]

    # GENERAL ENDPOINTS

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-connectivity
    async def ping(self):
        return await self.http.send_api_call("/api/v3/ping", signed=False)

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#check-server-time
    async def fetch_server_time(self):
        return await self.http.send_api_call("/api/v3/time", signed=False)

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#exchange-information
    async def fetch_exchange_info(self):
        return await self.http.send_api_call("/api/v3/exchangeInfo", signed=False)

    # MARKET DATA ENDPOINTS

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book
    async def fetch_order_book(self, symbol, limit=100):
        if limit == 100:
            return await self.http.send_api_call(
                "/api/v3/depth", params={"symbol": symbol}, signed=False
            )
        else:
            return await self.http.send_api_call(
                "/api/v3/depth", params={"symbol": symbol, "limit": limit}, signed=False
            )
