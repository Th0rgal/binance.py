import aiohttp


class HttpClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session = aiohttp.ClientSession()

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#exchange-information
    async def fetch_exchange_info(self):
        return await self.send_api_call("/api/v3/exchangeInfo")

    async def send_api_call(self, path, method="GET", **kwargs):
        # return the JSON body of a call to Discord REST API
        defaults = {"headers": {}}  # X-MBX-APIKEY
        kwargs = dict(defaults, **kwargs)
        async with self.session as session:
            async with session.request(
                method, self.endpoint + path, **kwargs,
            ) as response:
                assert response.status >= 200 and response.status < 300, response.reason
                if response.status != 204:
                    return await response.json()
