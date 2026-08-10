from market_data.instrument_loader import (
    NSEInstrumentLoader,
)


loader = NSEInstrumentLoader()

loader.load()

stocks = loader.get_nse_equities()

print(
    f"\nNSE equity instruments: "
    f"{len(stocks):,}"
)

print("\nFirst 20:")

for stock in stocks[:20]:

    print(
        f"{stock['symbol']:<15} "
        f"Token: {stock['token']}"
    )


print("\nRELIANCE lookup:")

for stock in stocks:

    if stock["symbol"] == "RELIANCE":

        print(stock)
        break