import aiohttp, time
from .http import HttpClient
from . import OrderType


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
        return await self.http.send_api_call("/api/v3/ping", send_api_key=False)

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#check-server-time
    async def fetch_server_time(self):
        return await self.http.send_api_call("/api/v3/time", send_api_key=False)

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#exchange-information
    async def fetch_exchange_info(self):
        return await self.http.send_api_call("/api/v3/exchangeInfo", send_api_key=False)

    # MARKET DATA ENDPOINTS

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book
    async def fetch_order_book(self, symbol, limit=100):
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        if limit == 100:
            return await self.http.send_api_call(
                "/api/v3/depth", params={"symbol": symbol}
            )
        elif limit in valid_limits:
            return await self.http.send_api_call(
                "/api/v3/depth",
                params={"symbol": symbol, "limit": limit},
                send_api_key=False,
            )
        else:
            raise ValueError(
                f"{limit} is not a valid limit. Valid limits: {valid_limits}"
            )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list
    async def fetch_recent_trades_list(self, symbol, limit=500):
        if limit == 500:
            params = {"symbol": symbol}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "limit": limit}
        else:
            raise ValueError(
                f"{limit} is not a valid limit. A valid limit should be > 0 and < to 1000."
            )
        return await self.http.send_api_call(
            "/api/v3/trades", params=params, signed=False
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#old-trade-lookup-market_data
    async def fetch_old_trades_list(self, symbol, from_id=None, limit=500):
        if limit == 500:
            params = {"symbol": symbol}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "limit": limit}
        else:
            raise ValueError(
                f"{limit} is not a valid limit. A valid limit should be > 0 and < to 1000."
            )
        if from_id:
            params["fromId"] = from_id
        return await self.http.send_api_call(
            "/api/v3/historicalTrades", params=params, signed=False
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#compressedaggregate-trades-list
    async def fetch_aggregate_trades_list(
        self, symbol, from_id=0, start_time=0, end_time=0, limit=500
    ):
        if limit == 500:
            params = {"symbol": symbol}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "limit": limit}
        else:
            raise ValueError(
                f"{limit} is not a valid limit. A valid limit should be > 0 and < to 1000."
            )
        if from_id:
            params["fromId"] = from_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self.http.send_api_call(
            "/api/v3/aggTrades", params=params, signed=False
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data
    async def fetch_klines(self, symbol, interval, start_time=0, end_time=0, limit=500):
        if limit == 500:
            params = {"symbol": symbol, "interval": interval}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "interval": interval, "limit": limit}
        else:
            raise ValueError(
                f"{limit} is not a valid limit. A valid limit should be > 0 and < to 1000."
            )
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self.http.send_api_call(
            "/api/v3/klines", params=params, signed=False
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-average-price
    async def fetch_average_price(self, symbol):
        return await self.http.send_api_call(
            "/api/v3/avgPrice",
            params={"symbol": symbol},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics
    async def fetch_ticker_price_change_statistics(self, symbol=None):
        return await self.http.send_api_call(
            "/api/v3/avgPrice",
            params={"symbol": symbol} if symbol else {},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-price-ticker
    async def fetch_symbol_price_ticker(self, symbol=None):
        return await self.http.send_api_call(
            "/api/v3/ticker/price",
            params={"symbol": symbol} if symbol else {},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-order-book-ticker
    async def fetch_symbol_order_book_ticker(self, symbol=None):
        return await self.http.send_api_call(
            "/api/v3/ticker/bookTicker",
            params={"symbol": symbol} if symbol else {},
            signed=False,
            send_api_key=False,
        )

    # ACCOUNT ENDPOINTS

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade
    async def create_order(
        self,
        symbol,
        side,
        order_type,
        time_in_force=None,
        quantity=None,
        quote_order_quantity=None,
        price=None,
        new_client_order_id=None,
        stop_price=None,
        iceberg_quantity=None,
        new_order_response_type=None,
        receive_window=None,
        test=False,
    ):
        params = {"symbol": symbol, "side": side, "type": order_type}

        if time_in_force:
            params["timeInForce"] = time_in_force
        elif order_type in [
            OrderType.LIMIT,
            OrderType.STOP_LOSS_LIMIT,
            OrderType.TAKE_PROFIT_LIMIT,
        ]:
            raise ValueError("This order type requires you to specify time_in_force.")

        if quote_order_quantity:
            params["quoteOrderQty"] = quote_order_quantity
        if quantity:
            params["quantity"] = quantity
        elif not quote_order_quantity:
            raise ValueError(
                "You need to specify a quantity or a quote_order_quantity."
                if order_type == OrderType.MARKET
                else "You need to specify a quantity."
            )

        if price:
            params["price"] = price
        elif order_type in [
            OrderType.LIMIT,
            OrderType.STOP_LOSS_LIMIT,
            OrderType.TAKE_PROFIT_LIMIT,
            OrderType.LIMIT_MAKER,
        ]:
            raise ValueError("This order type requires you to specify a price.")

        if new_client_order_id:
            params["newClientOrderId"] = new_client_order_id
        if stop_price:
            params["stopPrice"] = stop_price
        if iceberg_quantity:
            params["icebergQty"] = iceberg_quantity
        if new_order_response_type:
            params["newOrderRespType"] = new_order_response_type
        if receive_window:
            params["recvWindow"] = receive_window

        route = "/api/v3/order/test" if test else "/api/v3/order"
        return await self.http.send_api_call(route, "POST", data=params, signed=True)
