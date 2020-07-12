# Enum definitions of the binance REST API
# see: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#enum-definitions
from enum import Enum

# Symbol status (status)
class SymbolStatus(Enum):
    PRE_TRADING = "PRE_TRADING"
    TRADING = "TRADING"
    POST_TRADING = "POST_TRADING"
    END_OF_DAY = "END_OF_DAY"
    HALT = "HALT"
    AUCTION_MATCH = "AUCTION_MATCH"
    BREAK = "BREAK"


# Symbol type:
class SymbolType(Enum):
    SPOT = "SPOT"


# Order status (status):
class OrderStatus(Enum):
    NEW = "NEW"  # The order has been accepted by the engine.
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # A part of the order has been filled.
    FILLED = "FILLED"  # The order has been completely filled.
    CANCELED = "CANCELED"  # The order has been canceled by the user.
    PENDING_CANCEL = "PENDING_CANCEL"  # (currently unused)
    REJECTED = "REJECTED"  # The order was not accepted by the engine and not processed.
    EXPIRED = "EXPIRED"  # The order was canceled according to the order type's rules
    # (e.g. LIMIT FOK orders with no fill, LIMIT IOC or MARKET orders that partially
    # fill) or by the exchange, (e.g. orders canceled during liquidation, orders
    # canceled during maintenance)


# OCO Status (listStatusType):
class ListStatusType(Enum):
    RESPONSE = "RESPONSE"
    EXEC_STARTED = "EXEC_STARTED"
    ALL_DONE = "ALL_DONE"


# OCO Order Status (listOrderStatus):
class ListOrderStatus(Enum):
    EXECUTING = "EXECUTING"
    ALL_DONE = "ALL_DONE"
    REJECT = "REJECT"


# ContingencyType
class ContingencyType(Enum):
    OCO = "OCO"


# Order types (orderTypes, type)
class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    LIMIT_MAKER = "LIMIT_MAKER"


class ResponseType(Enum):
    ACK = "ACK"
    RESULT = "RESULT"
    FULL = "FULL"


# Order side (side)
class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


# Time in force (timeInForce)
class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


# Kline/Candlestick chart intervals
# m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
class Interval(Enum):
    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTY_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    SIX_HOURS = "6h"
    HEIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    THREE_DAY = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"
