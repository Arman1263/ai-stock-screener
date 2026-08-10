from config.settings import (
    MIN_STOCK_PRICE,
    MAX_STOCK_PRICE,
    MIN_BID_QUANTITY,
    MIN_ASK_QUANTITY,
)


class StockScreener:

    def __init__(self):

        self.min_price = MIN_STOCK_PRICE
        self.max_price = MAX_STOCK_PRICE

        self.min_bid_quantity = MIN_BID_QUANTITY
        self.min_ask_quantity = MIN_ASK_QUANTITY

    def passes_filter(self, tick):

        price_ok = (
            self.min_price
            <= tick.ltp
            <= self.max_price
        )

        liquidity_ok = (
            tick.total_buy_quantity
            > self.min_bid_quantity
            and
            tick.total_sell_quantity
            > self.min_ask_quantity
        )

        return price_ok and liquidity_ok