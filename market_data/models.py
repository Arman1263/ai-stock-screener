from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketTick:

    symbol: str
    timestamp: datetime

    ltp: float
    ltq: int

    # Best bid/ask level
    bid_price: float
    bid_quantity: int

    ask_price: float
    ask_quantity: int

    # Total market depth quantities
    total_buy_quantity: int
    total_sell_quantity: int