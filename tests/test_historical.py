from market_data.angel_auth import AngelAuth
from market_data.historical import HistoricalData


auth = AngelAuth()

print("Logging into Angel One...")

auth.login()

print("Login successful.")

historical = HistoricalData(
    auth.smart_api
)

closes = historical.get_close_prices(
    symbol_token="2885",
    candles=150,
)

print(
    f"Received {len(closes)} historical closes."
)

print("\nLast 10 closes:")

for price in closes[-10:]:
    print(price)