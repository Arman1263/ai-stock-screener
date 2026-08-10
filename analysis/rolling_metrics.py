from datetime import timedelta


class RollingMetrics:

    def __init__(self, tick_store):
        self.tick_store = tick_store

    def _get_window_ticks(self, symbol, minutes):
        ticks = self.tick_store.get_ticks(symbol)

        if not ticks:
            return []

        cutoff = ticks[-1].timestamp - timedelta(minutes=minutes)

        return [
            tick for tick in ticks
            if tick.timestamp >= cutoff
        ]

    def get_etq(self, symbol, minutes):
        ticks = self._get_window_ticks(symbol, minutes)

        return sum(tick.ltq for tick in ticks)

    def get_average_ltp(self, symbol, minutes):
        ticks = self._get_window_ticks(symbol, minutes)

        if not ticks:
            return None

        return sum(tick.ltp for tick in ticks) / len(ticks)

    def get_average_ltq(self, symbol, minutes):
        ticks = self._get_window_ticks(symbol, minutes)

        if not ticks:
            return None

        return sum(tick.ltq for tick in ticks) / len(ticks)