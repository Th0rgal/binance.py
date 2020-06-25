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

outbound_account_info_handlers = Handlers()
outbound_account_position_handlers = Handlers()
balance_update_handlers = Handlers()
order_update_handlers = Handlers()
list_status_handlers = Handlers()


def wrap_event(event_data):

    events_by_name = {
        "outboundAccountInfo": OutboundAccountInfoWrapper,
        "outboundAccountInfo": OutboundAccountPositionWrapper,
        "balanceUpdate": BalanceUpdateWrapper,
        "orderUpdate": OrderUpdateWrapper,
        "listStatus": ListStatus,
    }

    return events_by_name[event_data["e"]](event_data)


def fire_event(wrapped_event):
    handlers_by_event = {
        OutboundAccountInfoWrapper: outbound_account_info_handlers,
        OutboundAccountPositionWrapper: outbound_account_position_handlers,
        BalanceUpdateWrapper: balance_update_handlers,
        OrderUpdateWrapper: order_update_handlers,
        ListStatus: list_status_handlers,
    }
    for event_class in handlers_by_event:
        if isinstance(wrapped_event, event_class):
            handlers_by_event[event_class].__call__(wrap_event)


class BinanceEventWrapper:
    def __init__(self, event_data):
        pass

    def fire(self):
        self.handlers.__call__(self)


# ACCOUNT UPDATE


class OutboundAccountInfoWrapper(BinanceEvent):
    def __init__(self, event_data):
        pass


class OutboundAccountPositionWrapper(BinanceEvent):
    def __init__(self, event_data):
        pass


# BALANCE UPDATE


class BalanceUpdateWrapper(BinanceEvent):
    def __init__(self, event_data):
        pass


# ORDER UPDATE


class OrderUpdateWrapper(BinanceEvent):
    def __init__(self, event_data):
        pass


class ListStatus(BinanceEvent):
    def __init__(self, event_data):
        pass
