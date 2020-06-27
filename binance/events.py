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
        self.outbound_account_info_handlers = Handlers()
        self.outbound_account_position_handlers = Handlers()
        self.balance_update_handlers = Handlers()
        self.order_update_handlers = Handlers()
        self.list_status_handlers = Handlers()

    def wrap_event(self, event_data):

        events_by_name = {
            "outboundAccountInfo": (
                OutboundAccountInfoWrapper,
                self.outbound_account_info_handlers,
            ),
            "outboundAccountPosition": (
                OutboundAccountPositionWrapper,
                self.outbound_account_position_handlers,
            ),
            "balanceUpdate": (BalanceUpdateWrapper, self.balance_update_handlers),
            "executionReport": (OrderUpdateWrapper, self.order_update_handlers),
            "listStatus": (ListStatus, self.list_status_handlers),
        }
        wrapper, handlers = events_by_name[event_data["e"]]
        return wrapper(event_data, handlers)


class BinanceEventWrapper:
    def __init__(self, event_data, handlers):
        self.handlers = handlers
        self.event_time = event_data["E"]

    def fire(self):
        self.handlers.__call__(self)


# ACCOUNT UPDATE


class OutboundAccountInfoWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
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
        self.last_update = event_data["u"]
        self.balances = dict(
            map(lambda x: (x["a"], {"free": x["f"], "locked": x["l"]}), event_data["B"])
        )


# BALANCE UPDATE


class BalanceUpdateWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
        self.asset = event_data["a"]
        self.balance_delta = event_data["d"]
        self.clear_time = event_data["T"]


# ORDER UPDATE


class OrderUpdateWrapper(BinanceEventWrapper):
    def __init__(self, event_data, handlers):
        super().__init__(event_data, handlers)
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
