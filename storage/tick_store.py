from collections import defaultdict, deque
from datetime import datetime, timedelta

from market_data.models import MarketTick


class TickStore:

    def __init__(self, retention_minutes: int = 60):
        self.retention_minutes = retention_minutes

        # Each symbol gets its own deque of MarketTick objects.
        self._ticks = defaultdict(deque)

    def add_tick(self, tick: MarketTick) -> None:
        """Store a new market tick and remove expired ticks."""

        self._ticks[tick.symbol].append(tick)

        self._remove_expired_ticks(
            symbol=tick.symbol,
            current_time=tick.timestamp,
        )

    def _remove_expired_ticks(
        self,
        symbol: str,
        current_time: datetime,
    ) -> None:

        cutoff_time = current_time - timedelta(
            minutes=self.retention_minutes
        )

        symbol_ticks = self._ticks[symbol]

        while (
            symbol_ticks
            and symbol_ticks[0].timestamp < cutoff_time
        ):
            symbol_ticks.popleft()

    def get_ticks(self, symbol: str):
        """Return all retained ticks for a symbol."""

        return list(self._ticks.get(symbol, []))

    def get_latest_tick(self, symbol: str):
        """Return the latest tick for a symbol."""

        symbol_ticks = self._ticks.get(symbol)

        if not symbol_ticks:
            return None

        return symbol_ticks[-1]

    def get_tick_count(self, symbol: str) -> int:
        """Return number of retained ticks."""

        return len(self._ticks.get(symbol, []))