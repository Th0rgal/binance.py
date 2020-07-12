from urllib.parse import urlencode
from . import __version__
import logging
import aiohttp
import hashlib
import hmac
import time
from .errors import (
    RateLimitReached,
    BinanceError,
    WAFLimitViolated,
    IPAdressBanned,
    HTTPError,
    QueryCanceled,
)


class HttpClient:
    def __init__(self, api_key, api_secret, endpoint, user_agent):
        self.api_key = api_key
        self.api_secret = api_secret
        self.endpoint = endpoint
        self.rate_limit_reached = False
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"binance.py (https://git.io/binance.py, {__version__})"

    def _generate_signature(self, data):
        return hmac.new(
            self.api_secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256,
        ).hexdigest()

    async def handle_errors(self, response):
        if response.status >= 500:
            logging.error(
                "An issue occured on Binance's side; the execution status is UNKNOWN and could have been a success"
            )
        if response.status == 429:
            self.rate_limit_reached = True
            raise RateLimitReached()
        payload = await response.json()
        if payload and "code" in payload:
            # as defined here: https://github.com/binance-exchange/binance-official-api-docs/blob/master/errors.md#error-codes-for-binance-2019-09-25
            raise BinanceError(payload["msg"])
        if response.status >= 400:
            if response.status == 403:
                raise WAFLimitViolated()
            elif response.status == 418:
                raise IPAdressBanned()
            else:
                raise HTTPError("Malformed request. The issue is on the sender's side")
        return payload

    async def send_api_call(
        self, path, method="GET", signed=False, send_api_key=True, **kwargs
    ):
        if self.rate_limit_reached:
            raise QueryCanceled(
                "Rate limit reached, to avoid an IP ban, this query has been automatically cancelled"
            )
        # return the JSON body of a call to Binance REST API
        kwargs = dict({"headers": {"User-Agent": self.user_agent}}, **kwargs,)
        if send_api_key:
            kwargs["headers"]["X-MBX-APIKEY"] = self.api_key

        if signed:
            content = ""
            location = "params" if "params" in kwargs else "data"
            kwargs[location]["timestamp"] = int(time.time() * 1000)
            if "params" in kwargs:
                content += urlencode(kwargs["params"])
            if "data" in kwargs:
                content += urlencode(kwargs["data"])
            kwargs[location]["signature"] = self._generate_signature(content)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, self.endpoint + path, **kwargs,
            ) as response:
                return await self.handle_errors(response)
