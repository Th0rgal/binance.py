from .http import HttpClient
from .errors import BinancePyError
from .web_sockets import UserEventsDataStream, MarketEventsDataStream
from . import OrderType
from .events import Events
from enum import Enum


class Client:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        *,
        endpoint="https://api.binance.com",
        user_agent=None,
    ):
        if api_secret + api_secret == 1:
            raise ValueError(
                "You cannot only specify a non empty api_key or an api_secret."
            )
        self.http = HttpClient(api_key, api_secret, endpoint, user_agent)
        self.user_agent = user_agent
        self.loaded = False

    async def load(self):
        infos = await self.fetch_exchange_info()

        # load available symbols
        self.symbols = dict(map(lambda x: (x.pop("symbol"), x), infos["symbols"]))

        # load rate limits
        self.rate_limits = infos["rateLimits"]

        self.loaded = True

    @property
    def events(self):
        if not hasattr(self, "_events"):
            self._events = Events()
        return self._events

    async def start_user_events_listener(
        self, endpoint="wss://stream.binance.com:9443"
    ):
        self.user_data_stream = UserEventsDataStream(self, endpoint, self.user_agent)
        await self.user_data_stream.start()

    async def start_market_events_listener(
        self, endpoint="wss://stream.binance.com:9443"
    ):
        self.market_data_stream = MarketEventsDataStream(
            self, endpoint, self.user_agent
        )
        await self.market_data_stream.start()

    def assert_symbol_exists(self, symbol):
        if self.loaded:
            if symbol not in self.symbols:
                raise BinancePyError(
                    f"Symbol {symbol} is not valid according to the loaded exchange infos."
                )

    def round(self, symbol, amount):
        if self.loaded:
            precision = self.symbols[symbol]["baseAssetPrecision"]
            return f"%.{precision}f" % round(amount, precision)
        return amount

    def assert_symbol(self, symbol):
        if not symbol:
            raise ValueError("This query requires a symbol.")
        self.assert_symbol_exists(symbol)

    # keep support for hardcoded string but allow enums usage
    def enum_to_value(self, enum):
        if isinstance(enum, Enum):
            enum = enum.value
        return enum

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
        self.assert_symbol(symbol)
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
        self.assert_symbol(symbol)
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
        self.assert_symbol(symbol)
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
        self, symbol, from_id=None, start_time=None, end_time=None, limit=500
    ):
        self.assert_symbol(symbol)
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
    async def fetch_klines(
        self, symbol, interval, start_time=None, end_time=None, limit=500
    ):
        self.assert_symbol(symbol)
        interval = self.enum_to_value(interval)
        if not interval:
            raise ValueError("This query requires an interval.")
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
        self.assert_symbol(symbol)
        return await self.http.send_api_call(
            "/api/v3/avgPrice",
            params={"symbol": symbol},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics
    async def fetch_ticker_price_change_statistics(self, symbol=None):
        if symbol:
            self.assert_symbol_exists(symbol)
        return await self.http.send_api_call(
            "/api/v3/avgPrice",
            params={"symbol": symbol} if symbol else {},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-price-ticker
    async def fetch_symbol_price_ticker(self, symbol=None):
        if symbol:
            self.assert_symbol_exists(symbol)
        return await self.http.send_api_call(
            "/api/v3/ticker/price",
            params={"symbol": symbol} if symbol else {},
            signed=False,
            send_api_key=False,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-order-book-ticker
    async def fetch_symbol_order_book_ticker(self, symbol=None):
        if symbol:
            self.assert_symbol_exists(symbol)
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
        response_type=None,
        receive_window=None,
        test=False,
    ):
        self.assert_symbol(symbol)
        side = self.enum_to_value(side)
        order_type = self.enum_to_value(order_type)
        if not side:
            raise ValueError("This query requires a side.")
        if not order_type:
            raise ValueError("This query requires an order_type.")
        params = {"symbol": symbol, "side": side, "type": order_type}

        if time_in_force:
            params["timeInForce"] = self.enum_to_value(time_in_force)
        elif order_type in [
            OrderType.LIMIT.value,
            OrderType.STOP_LOSS_LIMIT.value,
            OrderType.TAKE_PROFIT_LIMIT.value,
        ]:
            raise ValueError("This order type requires a time_in_force.")

        if quote_order_quantity:
            params["quoteOrderQty"] = self.round(symbol, quote_order_quantity)
        if quantity:
            params["quantity"] = self.round(symbol, quantity)
        elif not quote_order_quantity:
            raise ValueError(
                "This order type requires a quantity or a quote_order_quantity."
                if order_type == OrderType.MARKET
                else "This order type requires a quantity."
            )

        if price:
            params["price"] = self.round(symbol, price)
        elif order_type in [
            OrderType.LIMIT.value,
            OrderType.STOP_LOSS_LIMIT.value,
            OrderType.TAKE_PROFIT_LIMIT.value,
            OrderType.LIMIT_MAKER.value,
        ]:
            raise ValueError("This order type requires a price.")

        if new_client_order_id:
            params["newClientOrderId"] = new_client_order_id

        if stop_price:
            params["stopPrice"] = self.round(symbol, stop_price)
        elif order_type in [
            OrderType.STOP_LOSS.value,
            OrderType.STOP_LOSS_LIMIT.value,
            OrderType.TAKE_PROFIT.value,
            OrderType.TAKE_PROFIT_LIMIT.value,
        ]:
            raise ValueError("This order type requires a stop_price.")

        if iceberg_quantity:
            params["icebergQty"] = self.round(symbol, iceberg_quantity)
        if response_type:
            params["newOrderRespType"] = response_type
        if receive_window:
            params["recvWindow"] = receive_window

        route = "/api/v3/order/test" if test else "/api/v3/order"
        return await self.http.send_api_call(route, "POST", data=params, signed=True)

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-order-user_data
    async def fetch_order(  # lgtm [py/similar-function]
        self, symbol, order_id=None, origin_client_order_id=None, receive_window=None
    ):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if not order_id and not origin_client_order_id:
            raise ValueError(
                "This query requires an order_id or an origin_client_order_id."
            )
        if order_id:
            params["orderId"] = order_id
        if origin_client_order_id:
            params["originClientOrderId"] = origin_client_order_id
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/order", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-order-trade
    async def cancel_order(  # lgtm [py/similar-function]
        self,
        symbol,
        order_id=None,
        origin_client_order_id=None,
        new_client_order_id=None,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if not order_id and not origin_client_order_id:
            raise ValueError(
                "This query requires an order_id or an origin_client_order_id."
            )
        if order_id:
            params["orderId"] = order_id
        if origin_client_order_id:
            params["originClientOrderId"] = origin_client_order_id
        if new_client_order_id:
            params["newClientOrderId"] = origin_client_order_id
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/order", "DELETE", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-all-open-orders-on-a-symbol-trade
    async def cancel_all_orders(self, symbol, receive_window=None):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/openOrders", "DELETE", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-open-orders-user_data
    async def fetch_open_orders(self, symbol, receive_window=None):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/openOrders", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#all-orders-user_data
    async def fetch_all_orders(
        self,
        symbol,
        order_id=None,
        start_time=None,
        end_time=None,
        limit=500,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        if limit == 500:
            params = {"symbol": symbol}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "limit": limit}
        else:
            raise ValueError(
                f"{limit} is not a valid limit. A valid limit should be > 0 and < to 1000."
            )

        if order_id:
            params["orderId"] = order_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/allOrders", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-oco-trade
    async def create_oco(
        self,
        symbol,
        side,
        quantity,
        price,
        stop_price,
        list_client_order_id=None,
        limit_iceberg_quantity=None,
        stop_client_order_id=None,
        stop_limit_price=None,
        stop_iceberg_quantity=None,
        stop_limit_time_in_force=None,
        response_type=None,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        side = self.enum_to_value(side)
        if not side:
            raise ValueError("This query requires a side.")
        if not quantity:
            raise ValueError("This query requires a quantity.")
        if not price:
            raise ValueError("This query requires a price.")
        if not stop_price:
            raise ValueError("This query requires a stop_price.")

        params = {
            "symbol": symbol,
            "side": side,
            "quantity": self.round(symbol, quantity),
            "price": self.round(symbol, price),
            "stopPrice": self.round(symbol, stop_price),
        }

        if list_client_order_id:
            params["listClientOrderId"] = list_client_order_id
        if limit_iceberg_quantity:
            params["limitIcebergQty"] = self.round(symbol, limit_iceberg_quantity)
        if stop_client_order_id:
            params["stopLimitPrice"] = self.round(symbol, stop_client_order_id)
        if stop_iceberg_quantity:
            params["stopIcebergQty"] = self.round(symbol, stop_iceberg_quantity)
        if stop_limit_time_in_force:
            params["stopLimitTimeInForce"] = stop_limit_time_in_force
        if response_type:
            params["newOrderRespType"] = response_type
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/order/oco", "POST", data=params, signed=True
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-oco-user_data
    async def fetch_oco(  # lgtm [py/similar-function]
        self,
        symbol,
        order_list_id=None,
        origin_client_order_id=None,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if not order_list_id and not origin_client_order_id:
            raise ValueError(
                "This query requires an order_id or an origin_client_order_id."
            )
        if order_list_id:
            params["orderListId"] = order_list_id
        if origin_client_order_id:
            params["originClientOrderId"] = origin_client_order_id
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/orderList", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-oco-trade
    async def cancel_oco(  # lgtm [py/similar-function]
        self,
        symbol,
        order_list_id=None,
        list_lient_order_id=None,
        new_client_order_id=None,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        params = {"symbol": symbol}
        if not order_list_id and not list_lient_order_id:
            raise ValueError(
                "This query requires a order_list_id or a list_lient_order_id."
            )
        if order_list_id:
            params["orderListId"] = order_list_id
        if list_lient_order_id:
            params["listClientOrderId"] = list_lient_order_id
        if new_client_order_id:
            params["newClientOrderId"] = new_client_order_id
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/order/oco", "DELETE", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-open-oco-user_data
    async def fetch_open_oco(self, receive_window=None):
        params = {}

        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/openOrderList", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-all-oco-user_data
    async def fetch_all_oco(
        self,
        from_id=None,
        start_time=None,
        end_time=None,
        limit=None,
        receive_window=None,
    ):
        params = {}

        if from_id:
            params["fromId"] = from_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if limit:
            params["limit"] = limit
        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/allOrderList", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data
    async def fetch_account_information(self, receive_window=None):
        params = {}

        if receive_window:
            params["recvWindow"] = receive_window

        return await self.http.send_api_call(
            "/api/v3/account", params=params, signed=True,
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-trade-list-user_data
    async def fetch_account_trade_list(
        self,
        symbol,
        start_time=None,
        end_time=None,
        from_id=None,
        limit=500,
        receive_window=None,
    ):
        self.assert_symbol(symbol)
        if limit == 500:
            params = {"symbol": symbol}
        elif limit > 0 and limit < 1000:
            params = {"symbol": symbol, "limit": limit}

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if from_id:
            params["fromId"] = from_id
        if receive_window:
            params["recvWindow"] = receive_window
        return await self.http.send_api_call(
            "/api/v3/myTrades", params=params, signed=True,
        )

    # USER DATA STREAM ENDPOINTS

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md#create-a-listenkey
    async def create_listen_key(self):
        return await self.http.send_api_call("/api/v3/userDataStream", "POST")

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md#close-a-listenkey
    async def keep_alive_listen_key(self, listen_key):
        if not listen_key:
            raise ValueError("This query requires a listen_key.")
        return await self.http.send_api_call(
            "/api/v3/userDataStream", "PUT", params={"listenKey": listen_key}
        )

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md#close-a-listenkey
    async def close_listen_key(self, listen_key):
        if not listen_key:
            raise ValueError("This query requires a listen_key.")
        return await self.http.send_api_call(
            "/api/v3/userDataStream", "DELETE", params={"listenKey": listen_key}
        )
