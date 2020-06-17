import aiohttp, hashlib, hmac, time
from urllib.parse import urlencode


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

    async def send_api_call(self, path, method="GET", signed=True, **kwargs):
        # return the JSON body of a call to Binance REST API

        if signed:
            kwargs = dict({"headers": {"X-MBX-APIKEY": self.api_key}}, **kwargs)
            kwargs["json"]["timestamp"] = int(time.time() * 1000)
            kwargs["json"]["signature"] = self._generate_signature(kwargs["json"])

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, self.endpoint + path, **kwargs,
            ) as response:
                # todo: manage response.status and response.reason
                return await response.json()
