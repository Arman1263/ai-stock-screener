import json
import urllib.request


INSTRUMENT_URL = (
    "https://margincalculator.angelbroking.com/"
    "OpenAPI_File/files/OpenAPIScripMaster.json"
)


class NSEInstrumentLoader:

    def __init__(self):
        self.instruments = []

    def load(self):

        print("Downloading Angel One instrument master...")

        with urllib.request.urlopen(
            INSTRUMENT_URL,
            timeout=30,
        ) as response:

            data = response.read()

        self.instruments = json.loads(data)

        print(
            f"Loaded {len(self.instruments):,} instruments."
        )

        return self.instruments

    def get_nse_equities(self):

        equities = []

        for instrument in self.instruments:

            if instrument.get("exch_seg") != "NSE":
                continue

            symbol = instrument.get("symbol", "")

            # We only want normal NSE equity instruments
            if not symbol.endswith("-EQ"):
                continue

            equities.append({
                "symbol": symbol.replace("-EQ", ""),
                "token": str(
                    instrument["token"]
                ),
                "exchange": "NSE",
            })

        return equities



    def get_token_map(self):

        equities = self.get_nse_equities()

        return {
            item["token"]: item["symbol"]
            for item in equities
        }