from collections import deque


class MarketHistory:

    def __init__(self, max_signals=100, max_trades=100):
        self.signals = deque(maxlen=max_signals)
        self.trades = deque(maxlen=max_trades)

    def add_signal(
        self,
        symbol,
        timestamp,
        price,
        signal,
        prediction,
    ):
        record = {
            "timestamp": timestamp,
            "symbol": symbol,
            "price": price,
            "signal": signal,
            "probability": (
                prediction["confidence_pct"]
                if prediction
                else None
            ),
            "decision": (
                prediction["decision"]
                if prediction
                else "N/A"
            ),
            "reasons": (
                prediction["reasons"]
                if prediction
                else []
            ),
        }

        self.signals.appendleft(record)

    def add_trade(self, symbol, trade):
        record = {
            "symbol": symbol,
            "direction": trade["direction"],
            "entry_time": trade["entry_time"],
            "exit_time": trade["exit_time"],
            "entry_price": trade["entry_price"],
            "exit_price": trade["exit_price"],
            "pnl": trade["pnl"],
            "profitable": trade["profitable"],
        }

        self.trades.appendleft(record)

    def get_signals(self):
        return list(self.signals)

    def get_trades(self):
        return list(self.trades)