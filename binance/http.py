import aiohttp, hashlib, hmac, time
from operator import itemgetter
from urllib.parse import urlencode
from . import __version__
import logging


class HttpClient:
    def __init__(self, api_key, api_secret, endpoint, user_agent=None):
        self.api_key = api_secret
        self.api_secret = api_secret
        self.endpoint = endpoint
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"binance.py (https://git.io/binance, {__version__})"

    def _generate_signature(self, data):
        query_string = urlencode(data)
        m = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        )
        return m.hexdigest()

    def _order_params(self, data):
        """Convert params to list with signature as last element
        :param data:
        :return:
        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == "signature":
                has_signature = True
            else:
                params.append((key, value))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(("signature", data["signature"]))
        return params

    async def handle_errors(self, response):
        if response.status >= 500:
            logging.error(
                "An issue occured on Binance's side; the execution status is UNKNOWN and could have been a success"
            )
        payload = await response.json()
        if payload and "code" in payload:
            # as defined here: https://github.com/binance-exchange/binance-official-api-docs/blob/master/errors.md#error-codes-for-binance-2019-09-25
            raise BinanceError(payload["msg"])
        if response.status >= 400:
            if response.status == 403:
                raise WAFLimitViolated()
            elif response.status == 429:
                raise RateLimitReached()
            elif response.status == 418:
                raise IPAdressBanned()
            else:
                raise HTTPError("Malformed request. The issue is on the sender's side")
        return payload

    async def send_api_call(
        self, path, method="GET", signed=False, send_api_key=True, **kwargs
    ):
        # return the JSON body of a call to Binance REST API
        kwargs = dict({"headers": {"User-Agent": self.user_agent}}, **kwargs,)
        if send_api_key:
            kwargs["headers"]["X-MBX-APIKEY"] = self.api_key
        data = kwargs.get("data", None)

        if data and isinstance(data, dict):
            kwargs["data"] = data

            # find any requests params passed and apply them
            if "params" in kwargs:
                # merge requests params into kwargs
                kwargs["data"].update(kwargs["params"])
                del kwargs["params"]
        if signed:
            kwargs["data"]["timestamp"] = int(time.time() * 1000)
            data = self._order_params(kwargs["data"])
            print(kwargs)
            kwargs["data"]["signature"] = self._generate_signature(data)
            print(kwargs)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, self.endpoint + path, **kwargs,
            ) as response:
                return await self.handle_errors(response)


class BinanceError(Exception):
    pass


class HTTPError(Exception):

    code = 400
    message = "Malformed request."


class WAFLimitViolated(HTTPError):

    code = 403
    message = "The WAF Limit (Web Application Firewall) has been violated."


class RateLimitReached(HTTPError):

    code = 429
    message = "The rate limit has been reached."


class IPAdressBanned(HTTPError):

    code = 418
    message = "Your IP address has been auto-banned for continuing to send requests after receiving 429 codes."
