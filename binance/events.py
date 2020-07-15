from collections import defaultdict
from .errors import UnknownEventType

# based on: https://stackoverflow.com/a/2022629/10144963
class Handlers(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Handlers(%s)" % list.__repr__(self)


# HANDLERS
# Example usage:

# from binance import events
#
# def my_order_update_listener(wrapped_event):
#    print(f"order for symbol {wrapped_event.symbol} updated!")
#
# events.order_update_handlers.append(my_order_update_listener)


class Events:
    def __init__(self):
        self.handlers = defaultdict(Handlers)
        self.registered_streams = set()

    def register_user_event(self, listener, event_type):
        self.handlers[event_type].append(listener)

    def register_event(self, listener, event_type):
        self.registered_streams.add(event_type)
        self.handlers[event_type].append(listener)

    def unregister(self, listener, event_type):
        self.handlers[event_type].remove(listener)

    def wrap_event(self, event_data):
        wrapper_by_type = {
            "outboundAccountInfo": OutboundAccountInfoWrapper,
            "outboundAccountPosition": OutboundAccountPositionWrapper,
            "balanceUpdate": BalanceUpdateWrapper,
            "executionReport": OrderUpdateWrapper,
            "listStatus": ListStatus,
            "aggTrade": AggregateTradeWrapper,
            "trade": TradeWrapper,
            "kline": KlineWrapper,
            "24hrMiniTicker": SymbolMiniTickerWrapper,
            "24hrTicker": SymbolTickerWrapper,
            "bookTicker": SymbolBookTickerWrapper,
            "depth5": PartialBookDepthWrapper,
            "depth10": PartialBookDepthWrapper,
            "depth20": PartialBookDepthWrapper,
            "depth": DiffDepthWrapper,
        }

        stream = event_data["stream"] if "stream" in event_data else False
        event_type = event_data["e"] if "e" in event_data else stream
        if "@" in event_type: # lgtm [py/member-test-non-container]
            event_type = event_type.split("@")[1]
        if event_type.startswith("kline_"):
            event_type = "kline"
        if event_type not in wrapper_by_type:
            raise UnknownEventType()
        wrapper = wrapper_by_type[event_type]
        return wrapper(event_data, self.handlers[stream if stream else event_type])


class BinanceEventWrapper:
    def __init__(self, event_data, handlers):
        self.handlers = handlers

    def fire(self):
        if self.handlers:
            self.handlers.__call__(self)


# MARKET EVENTS


class AggregateTradeWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers): # lgtm [py/similar-function]
        super().__init__(event_data, handlers)
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.aggregated_trade_id = event_data["a"]
        self.price = event_data["p"]
        self.quantity = event_data["q"]
        self.first_trade_id = event_data["f"]
        self.last_trade_id = event_data["l"]
        self.trade_time = event_data["T"]
        self.buyer_is_marker = event_data["m"]
        self.ignore = event_data["M"]


class TradeWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers): # lgtm [py/similar-function]
        super().__init__(event_data, handlers)
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.trade_id = event_data["t"]
        self.price = event_data["p"]
        self.quantity = event_data["q"]
        self.buyer_order_id = event_data["b"]
        self.seller_order_id = event_data["a"]
        self.trade_time = event_data["T"]
        self.buyer_is_marker = event_data["m"]
        self.ignore = event_data["M"]


class KlineWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        kline = event_data["k"]
        self.kline_start_time = kline["t"]
        self.kline_close_time = kline["T"]
        self.kline_symbol = kline["s"]
        self.kline_interval = kline["i"]
        self.kline_first_trade_id = kline["f"]
        self.kline_last_trade_id = kline["L"]
        self.kline_open_price = kline["o"]
        self.kline_close_price = kline["c"]
        self.kline_high_price = kline["h"]
        self.kline_low_price = kline["l"]
        self.kline_base_asset_volume = kline["v"]
        self.kline_trades_number = kline["n"]
        self.kline_closed = kline["x"]
        self.kline_quote_asset_volume = kline["q"]
        self.kline_taker_buy_base_asset_volume = kline["V"]
        self.kline_taker_buy_quote_asset_volume = kline["Q"]
        self.kline_ignore = kline["B"]


class SymbolMiniTickerWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers) # lgtm [py/similar-function]
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.close_price = event_data["c"]
        self.open_price = event_data["o"]
        self.high_price = event_data["h"]
        self.low_price = event_data["l"]
        self.total_traded_base_asset_volume = event_data["v"]
        self.total_traded_quote_asset_volume = event_data["q"]


class SymbolTickerWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.price_change = event_data["p"]
        self.price_change_percent = event_data["P"]
        self.weighted_average_price = event_data["w"]
        self.first_trade_before_window = event_data["x"]
        self.last_price = event_data["c"]
        self.last_quantity = event_data["Q"]
        self.best_bid_price = event_data["b"]
        self.best_bid_quantity = event_data["B"]
        self.best_ask_price = event_data["a"]
        self.best_ask_quantity = event_data["A"]
        self.open_price = event_data["o"]
        self.high_price = event_data["h"]
        self.low_price = event_data["l"]
        self.total_traded_base_asset_volume = event_data["v"]
        self.total_traded_quote_asset_volume = event_data["q"]
        self.statistics_open_time = event_data["O"]
        self.statistics_close_time = event_data["C"]
        self.first_trade_id = event_data["F"]
        self.last_trade_id = event_data["L"]
        self.total_trade_numbers = event_data["n"]


class SymbolBookTickerWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.order_book_updated = event_data["u"]
        self.symbol = event_data["s"]
        self.best_bid_price = event_data["b"]
        self.best_bid_quantity = event_data["B"]
        self.best_ask_price = event_data["a"]
        self.best_ask_quantity = event_data["A"]


class SymbolBookTickerWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.order_book_updated = event_data["u"]
        self.symbol = event_data["s"]
        self.best_bid_price = event_data["b"]
        self.best_bid_quantity = event_data["B"]
        self.best_ask_price = event_data["a"]
        self.best_ask_quantity = event_data["A"]


class PartialBookDepthWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.last_update_id = event_data["lastUpdateId"]
        self.bids = event_data["bids"]
        self.asks = event_data["asks"]


class DiffDepthWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_type = event_data["e"]
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.first_update_id = event_data["U"]
        self.final_update_id = event_data["u"]
        self.bids = event_data["b"]
        self.asks = event_data["a"]


# ACCOUNT UPDATE


class OutboundAccountInfoWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_time = event_data["E"]
        self.maker_commission_rate = event_data["m"]
        self.taker_commission_rate = event_data["t"]
        self.buyer_commission_rate = event_data["b"]
        self.seller_commission_rate = event_data["s"]
        self.can_trade = event_data["T"]
        self.can_withdraw = event_data["W"]
        self.can_deposit = event_data["D"]
        self.last_update = event_data["u"]
        self.balances = dict(
            map(lambda x: (x["a"], {"free": x["f"], "locked": x["l"]}), event_data["B"])
        )
        self.account_permissions = event_data["P"]


class OutboundAccountPositionWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_time = event_data["E"]
        self.last_update = event_data["u"]
        self.balances = dict(
            map(lambda x: (x["a"], {"free": x["f"], "locked": x["l"]}), event_data["B"])
        )


# BALANCE UPDATE


class BalanceUpdateWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_time = event_data["E"]
        self.asset = event_data["a"]
        self.balance_delta = event_data["d"]
        self.clear_time = event_data["T"]


# ORDER UPDATE


class OrderUpdateWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.client_order_id = event_data["c"]
        self.side = event_data["S"]
        self.order_type = event_data["o"]
        self.time_in_force = event_data["f"]
        self.order_quantity = event_data["q"]
        self.order_price = event_data["p"]
        self.stop_price = event_data["P"]
        self.iceberg_quantity = event_data["F"]
        self.order_list_id = event_data["g"]
        self.original_client_id = event_data["C"]
        self.execution_type = event_data["x"]
        self.order_status = event_data["X"]
        self.order_reject_reason = event_data["r"]
        self.order_id = event_data["i"]
        self.last_executed_quantity = event_data["l"]
        self.cumulative_filled_quantity = event_data["z"]
        self.last_executed_price = event_data["L"]
        self.commission_amount = event_data["n"]
        self.commission_asset = event_data["N"]
        self.transaction_time = event_data["T"]
        self.trade_id = event_data["t"]
        self.ignore_a = event_data["I"]
        self.in_order_book = event_data["w"]
        self.is_maker_side = event_data["m"]
        self.ignore_b = event_data["M"]
        self.order_creation_time = event_data["O"]
        self.quote_asset_transacted = event_data["Z"]
        self.last_quote_asset_transacted = event_data["Y"]
        self.quote_order_quantity = event_data["Q"]


class ListStatus(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.event_time = event_data["E"]
        self.symbol = event_data["s"]
        self.order_list_id = event_data["g"]
        self.contingency_type = event_data["c"]
        self.list_status_type = event_data["l"]
        self.list_order_status = event_data["L"]
        self.list_reject_reason = event_data["r"]
        self.list_client_order_id = event_data["C"]
        self.orders = dict(
            map(lambda x: (x["s"], {"orderid": x["i"], "clientorderid": x["c"]})),
            event_data["O"],
        )
