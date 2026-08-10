import time

from market_data.mock_provider import MockMarketDataProvider
from engine.processor import MarketProcessor


stocks = {
    "RELIANCE": 142.50,
    "TCS": 420.00,
    "INFY": 350.00,
    "SBIN": 480.00,
    "ITC": 250.00,
    "WIPRO": 290.00,
}


provider = MockMarketDataProvider(stocks)
processor = MarketProcessor()


# Connect to market-data provider
provider.connect()


try:

    while True:

        ticks = provider.generate_ticks()

        for tick in ticks:

            result = processor.process_tick(tick)

            # --------------------------------
            # Crossover + AI analysis
            # --------------------------------
            if result["signal"] and result["prediction"]:

                prediction = result["prediction"]

                print("\n" + "=" * 50)

                print(
                    f"{result['symbol']} "
                    f"{result['signal']} CROSSOVER "
                    f"@ ₹{result['ltp']:.2f}"
                )

                print("-" * 50)

                print(
                    f"AI Probability : "
                    f"{prediction['confidence_pct']}%"
                )

                print(
                    f"Decision       : "
                    f"{prediction['decision']}"
                )

                print("\nReasons:")

                for reason in prediction["reasons"]:
                    print(f"- {reason}")

                print(
                    f"\nStored signals : "
                    f"{len(processor.get_signal_history())}"
                )

                print("=" * 50)

            # --------------------------------
            # Completed trade history
            # --------------------------------
            trade_event = result["trade_event"]

            if (
                trade_event
                and trade_event["event"] == "CLOSE_AND_OPEN"
            ):

                trade = trade_event["closed_trade"]

                print("\n" + "-" * 50)
                print("COMPLETED TRADE")

                print(
                    f"{result['symbol']} | "
                    f"{trade['direction']}"
                )

                print(
                    f"Entry : ₹{trade['entry_price']:.2f}"
                )

                print(
                    f"Exit  : ₹{trade['exit_price']:.2f}"
                )

                print(
                    f"P/L   : ₹{trade['pnl']:.2f}"
                )

                print(
                    f"Result: "
                    f"{'PROFIT' if trade['profitable'] else 'LOSS'}"
                )

                print(
                    f"Completed trades: "
                    f"{len(processor.get_trade_history())}"
                )

                print("-" * 50)

        time.sleep(0.01)


finally:

    # Disconnect when application is stopped
    provider.disconnect()