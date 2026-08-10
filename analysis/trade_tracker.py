class TradeTracker:

    def __init__(self):
        self.active_trade = None
        self.completed_trades = []

    def process_signal(
        self,
        signal,
        price,
        timestamp,
        allow_entry=True,
    ):

        if signal is None:
            return None

        # ====================================================
        # NO ACTIVE TRADE
        # ====================================================

        if self.active_trade is None:

            # ML says AVOID -> don't open a trade
            if not allow_entry:
                return {
                    "event": "SKIP",
                    "signal": signal,
                }

            # ML says ACCEPT -> open trade
            self.active_trade = {
                "direction": signal,
                "entry_price": price,
                "entry_time": timestamp,
            }

            return {
                "event": "OPEN",
                **self.active_trade,
            }

        # ====================================================
        # SAME-DIRECTION SIGNAL
        # ====================================================

        if signal == self.active_trade["direction"]:
            return None

        # ====================================================
        # OPPOSITE SIGNAL
        # Close existing trade first
        # ====================================================

        trade = self.active_trade

        if trade["direction"] == "BUY":
            pnl = price - trade["entry_price"]

        else:
            pnl = trade["entry_price"] - price

        completed_trade = {
            "direction": trade["direction"],
            "entry_price": trade["entry_price"],
            "exit_price": price,
            "entry_time": trade["entry_time"],
            "exit_time": timestamp,
            "pnl": pnl,
            "profitable": pnl > 0,
        }

        self.completed_trades.append(
            completed_trade
        )

        # Existing position is now closed
        self.active_trade = None

        # ====================================================
        # ML DECISION FOR NEW OPPOSITE POSITION
        # ====================================================

        if not allow_entry:

            return {
                "event": "CLOSE",
                "closed_trade": completed_trade,
            }

        # ML ACCEPT -> immediately reverse position
        self.active_trade = {
            "direction": signal,
            "entry_price": price,
            "entry_time": timestamp,
        }

        return {
            "event": "CLOSE_AND_OPEN",
            "closed_trade": completed_trade,
            "new_trade": self.active_trade,
        }