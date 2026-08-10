import time

from market_data.angel_auth import AngelAuth
from market_data.angel_provider import AngelOneProvider


auth = AngelAuth()

print("Logging into Angel One...")

auth.login()

print("Login successful.")

provider = AngelOneProvider(auth)

provider.connect()

try:

    while True:

        ticks = provider.generate_ticks()

        for tick in ticks:

            print(
                f"\nMarketTick received:"
            )

            print(
                f"{tick.symbol} | "
                f"LTP ₹{tick.ltp:.2f} | "
                f"LTQ {tick.ltq} | "
                f"Bid ₹{tick.bid_price:.2f} "
                f"({tick.bid_quantity:,}) | "
                f"Ask ₹{tick.ask_price:.2f} "
                f"({tick.ask_quantity:,})"
            )

        time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping...")

finally:

    provider.disconnect()