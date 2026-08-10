from datetime import datetime, timedelta


class HistoricalData:

    def __init__(self, smart_api):
        self.smart_api = smart_api

    def get_close_prices(
        self,
        symbol_token,
        exchange="NSE",
        interval="FIVE_MINUTE",
        candles=150,
    ):

        end_time = datetime.now()
        start_time = end_time - timedelta(
            days=5
        )

        params = {
            "exchange": exchange,
            "symboltoken": str(symbol_token),
            "interval": interval,
            "fromdate": start_time.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "todate": end_time.strftime(
                "%Y-%m-%d %H:%M"
            ),
        }

        response = self.smart_api.getCandleData(
            params
        )

        if not response.get("status"):
            raise RuntimeError(
                f"Historical data failed: {response}"
            )

        data = response.get("data", [])

        if not data:
            raise RuntimeError(
                "No historical candle data returned."
            )

        # Angel One candle format:
        # [timestamp, open, high, low, close, volume]

        closes = [
            float(candle[4])
            for candle in data
        ]

        # We only need the latest candles.
        return closes[-candles:]