import time

from market_data.angel_auth import AngelAuth
from market_data.angel_provider import AngelOneProvider
from engine.processor import MarketProcessor


auth = AngelAuth()

print("Logging into Angel One...")
auth.login()
print("Login successful.")

provider = AngelOneProvider(auth)
processor = MarketProcessor()


try:

    provider.connect()

    print("Waiting for real market ticks...\n")

    while True:

        ticks = provider.generate_ticks()

        for tick in ticks:

            result = processor.process_tick(tick)

            if result["etq_5m"] > 0:

                print(
                    f"METRICS | "
                    f"{result['symbol']} | "
                    f"ETQ5 {result['etq_5m']} | "
                    f"ETQ20 {result['etq_20m']} | "
                    f"ETQ60 {result['etq_60m']} | "
                    f"Avg20 ₹{result['avg_ltp_20m']:.2f} | "
                    f"Avg60 ₹{result['avg_ltp_60m']:.2f}"
                )

            # --------------------------------
            # Screened stock
            # --------------------------------

            if result["passes_filter"]:

                print(
                    f"\n>>> SCREENED "
                    f"{result['symbol']} | "
                    f"LTP ₹{result['ltp']:.2f} | "
                    f"Buy "
                    f"{tick.total_buy_quantity:,} | "
                    f"Sell "
                    f"{tick.total_sell_quantity:,}"
                )

            # --------------------------------
            # Market data
            # --------------------------------

            smma20 = (
                f"{result['smma20']:.2f}"
                if result["smma20"] is not None
                else "-"
            )

            smma120 = (
                f"{result['smma120']:.2f}"
                if result["smma120"] is not None
                else "-"
            )

            print(
                f"{result['symbol']:<12} | "
                f"LTP ₹{result['ltp']:<8.2f} | "
                f"LTQ {result['ltq']:<8} | "
                f"Bid ₹{result['bid_price']:<8.2f} "
                f"({result['bid_quantity']:,}) | "
                f"Ask ₹{result['ask_price']:<8.2f} "
                f"({result['ask_quantity']:,}) | "
                f"SMMA20: {smma20:<8} | "
                f"SMMA120: {smma120:<8}"
            )

            # --------------------------------
            # Crossover
            # --------------------------------

            if result["signal"]:

                print(
                    f"\n>>> {result['signal']} "
                    f"CROSSOVER "
                    f"@ ₹{result['ltp']:.2f}"
                )

            # --------------------------------
            # AI prediction
            # --------------------------------

            if result["prediction"]:

                prediction = result["prediction"]

                print(
                    f"AI: "
                    f"{prediction['confidence_pct']}% | "
                    f"{prediction['decision']}"
                )

        time.sleep(0.1)


except KeyboardInterrupt:

    print("\nStopping application...")


finally:

    provider.disconnect()