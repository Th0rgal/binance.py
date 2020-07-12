class BinancePyError(Exception):
    pass


class UnknownEventType(BinancePyError):
    message = "BinancePy doesn't handle this event type"


class BinanceError(BinancePyError):
    pass


class QueryCanceled(BinancePyError):
    pass


class HTTPError(BinancePyError):

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
