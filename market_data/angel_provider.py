import threading
from collections import deque
from datetime import datetime

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from market_data.base_provider import MarketDataProvider
from market_data.models import MarketTick
from market_data.instrument_loader import NSEInstrumentLoader


class AngelOneProvider(MarketDataProvider):

    NSE_CM = 1
    SNAP_QUOTE = 3

    def __init__(self, auth):

        self.auth = auth

        self.ws = None
        self.thread = None
        self.connected = False

        self.ticks = deque(maxlen=5000)

        # --------------------------------
        # Load NSE instruments
        # --------------------------------

        loader = NSEInstrumentLoader()

        loader.load()

        self.token_map = loader.get_token_map()

        # --------------------------------
        # Temporary: first 20 NSE equities
        # --------------------------------

        stocks = loader.get_nse_equities()[:500]

        print(
            f"Prepared {len(stocks)} stocks "
            f"for WebSocket subscription."
        )

        print(
            "Sample stocks:",
            [stock["symbol"] for stock in stocks[:20]]
        )

        self.subscriptions = [
            {
                "exchangeType": self.NSE_CM,
                "tokens": [
                    stock["token"]
                    for stock in stocks
                ],
            }
        ]

        print(
            f"Prepared {len(stocks)} stocks "
            f"for WebSocket subscription."
        )

    def connect(self):

        print("Connecting to Angel One...")

        self.ws = SmartWebSocketV2(
            self.auth.auth_token,
            self.auth.api_key,
            self.auth.client_code,
            self.auth.feed_token,
        )

        self.ws.on_open = self._on_open
        self.ws.on_data = self._on_data
        self.ws.on_error = self._on_error
        self.ws.on_close = self._on_close

        self.thread = threading.Thread(
            target=self.ws.connect,
            daemon=True,
        )

        self.thread.start()

    def _on_open(self, wsapp):

        print(
            "Angel One WebSocket connected."
        )

        self.connected = True

        self.ws.subscribe(
            "ai_stock",
            self.SNAP_QUOTE,
            self.subscriptions,
        )

        print(
            "Subscribed to 20 NSE equities."
        )

    def _on_data(self, wsapp, data):

        try:

            if not data:
                return

            # --------------------------------
            # Identify stock
            # --------------------------------

            token = str(
                data.get("token", "")
            )

            symbol = self.token_map.get(
                token
            )

            if not symbol:

                print(
                    f"Unknown token received: "
                    f"{token}"
                )

                return

            # --------------------------------
            # Price
            # --------------------------------

            ltp = (
                data["last_traded_price"] / 100
            )

            ltq = int(
                data.get(
                    "last_traded_quantity",
                    0,
                )
            )

            # --------------------------------
            # Best 5 market depth
            # --------------------------------

            buy_data = data.get(
                "best_5_buy_data",
                [],
            )

            sell_data = data.get(
                "best_5_sell_data",
                [],
            )

            bid_price = 0.0
            bid_quantity = 0

            ask_price = 0.0
            ask_quantity = 0

            if buy_data:

                bid_price = (
                    buy_data[0]["price"] / 100
                )

                bid_quantity = int(
                    buy_data[0]["quantity"]
                )

            if sell_data:

                ask_price = (
                    sell_data[0]["price"] / 100
                )

                ask_quantity = int(
                    sell_data[0]["quantity"]
                )

            # --------------------------------
            # Total market liquidity
            # --------------------------------

            total_buy_quantity = int(
                data.get(
                    "total_buy_quantity",
                    0,
                )
            )

            total_sell_quantity = int(
                data.get(
                    "total_sell_quantity",
                    0,
                )
            )

            # --------------------------------
            # Timestamp
            # --------------------------------

            timestamp = datetime.now()

            # --------------------------------
            # Create MarketTick
            # --------------------------------

            tick = MarketTick(
                symbol=symbol,

                timestamp=timestamp,

                ltp=ltp,
                ltq=ltq,

                bid_price=bid_price,
                bid_quantity=bid_quantity,

                ask_price=ask_price,
                ask_quantity=ask_quantity,

                total_buy_quantity=(
                    total_buy_quantity
                ),

                total_sell_quantity=(
                    total_sell_quantity
                ),
            )

            self.ticks.append(tick)

            # --------------------------------
            # Console output
            # --------------------------------

            print(
                f"{symbol:<12} | "
                f"LTP ₹{ltp:<8.2f} | "
                f"LTQ {ltq:<6} | "
                f"Bid ₹{bid_price:<8.2f} "
                f"({bid_quantity:,}) | "
                f"Ask ₹{ask_price:<8.2f} "
                f"({ask_quantity:,}) | "
                f"Buy {total_buy_quantity:,} | "
                f"Sell {total_sell_quantity:,}"
            )

        except Exception as e:

            print(
                f"Error processing "
                f"Angel One tick: {e}"
            )

    def _on_error(self, wsapp, error):

        print(
            f"Angel One WebSocket error: "
            f"{error}"
        )

    def _on_close(self, wsapp):

        self.connected = False

        print(
            "Angel One WebSocket disconnected."
        )

    def generate_ticks(self):

        ticks = []

        while self.ticks:

            ticks.append(
                self.ticks.popleft()
            )

        return ticks

    def disconnect(self):

        if self.ws:

            print(
                "Disconnecting Angel One..."
            )

            self.ws.close_connection()

        self.connected = False