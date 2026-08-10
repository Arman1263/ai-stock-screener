import random
from datetime import datetime

from market_data.models import MarketTick
from market_data.base_provider import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):

    def __init__(self, stocks):
        self.prices = stocks.copy()

    def connect(self):
        print("Mock market data provider connected.")
        return True

    def disconnect(self):
        print("Mock market data provider disconnected.")

    def generate_ticks(self):

        ticks = []

        for symbol, current_price in self.prices.items():

            # Simulate price movement
            current_price += random.uniform(-0.50, 0.50)
            current_price = max(current_price, 1.0)

            self.prices[symbol] = current_price

            ltp = round(current_price, 2)

            # Simulate market spread
            spread = random.uniform(0.05, 0.30)

            tick = MarketTick(
                symbol=symbol,
                timestamp=datetime.now(),

                ltp=ltp,

                ltq=random.randint(
                    100,
                    10_000,
                ),

                bid_price=round(
                    ltp - spread,
                    2,
                ),

                bid_quantity=random.randint(
                    500_000,
                    2_000_000,
                ),

                ask_price=round(
                    ltp + spread,
                    2,
                ),

                ask_quantity=random.randint(
                    500_000,
                    2_000_000,
                ),
            )

            ticks.append(tick)

        return ticks