import aiohttp, hashlib, hmac, time
from urllib.parse import urlencode
import logging


class HttpClient:
    def __init__(self, api_key, api_secret, endpoint):
        self.api_key = api_secret
        self.api_secret = api_secret
        self.endpoint = endpoint

    def _generate_signature(self, data):
        print(data)
        query = urlencode(sorted(data.items()))
        print(query)
        return hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256,
        ).hexdigest()

    def handle_errors(self, response):
        if response.status >= 500:
            logging.error(
                "An issue occured on Binance's side; the execution status is UNKNOWN and could have been a success"
            )
        if response.status >= 400:
            if response.status == 403:
                raise WAFLimitViolated()
            elif response.status == 429:
                raise RateLimitReached()
            elif response.status == 418:
                raise IPAdressBanned()
            else:
                raise HTTPError("Malformed request. The issue is on the sender's side")
        payload = response.json()
        # as defined here: https://github.com/binance-exchange/binance-official-api-docs/blob/master/errors.md#error-codes-for-binance-2019-09-25
        if "code" in payload:
            raise BinanceError(payload["msg"])

    async def send_api_call(self, path, method="GET", signed=False, **kwargs):
        # return the JSON body of a call to Binance REST API

        if signed:
            kwargs = dict({"headers": {"X-MBX-APIKEY": self.api_key}}, **kwargs)
            kwargs["params"]["timestamp"] = int(time.time() * 1000)
            kwargs["params"]["signature"] = self._generate_signature(kwargs["params"])

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, self.endpoint + path, **kwargs,
            ) as response:
                # todo: manage response.status and response.reason
                return await response.json()


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
