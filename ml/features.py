class FeatureEngine:

    def __init__(self, metrics):
        self.metrics = metrics

    def create_features(self, tick, smma20, smma120, signal):

        if smma20 is None or smma120 is None:
            return None

        avg_ltq_2m = self.metrics.get_average_ltq(
            tick.symbol, 2
        )

        avg_ltq_5m = self.metrics.get_average_ltq(
            tick.symbol, 5
        )

        avg_ltp_20m = self.metrics.get_average_ltp(
            tick.symbol, 20
        )

        avg_ltp_60m = self.metrics.get_average_ltp(
            tick.symbol, 60
        )

        etq_5m = self.metrics.get_etq(
            tick.symbol, 5
        )

        etq_20m = self.metrics.get_etq(
            tick.symbol, 20
        )

        # Safe ratios
        ltq_ratio = (
            avg_ltq_2m / avg_ltq_5m
            if avg_ltq_5m
            else 0
        )

        etq_ratio = (
            etq_5m / etq_20m
            if etq_20m
            else 0
        )

        bid_ask_ratio = (
            tick.bid_quantity / tick.ask_quantity
            if tick.ask_quantity
            else 0
        )

        smma_distance_pct = (
            ((smma20 - smma120) / smma120) * 100
            if smma120
            else 0
        )

        price_vs_avg20 = (
            ((tick.ltp - avg_ltp_20m) / avg_ltp_20m) * 100
            if avg_ltp_20m
            else 0
        )

        price_vs_avg60 = (
            ((tick.ltp - avg_ltp_60m) / avg_ltp_60m) * 100
            if avg_ltp_60m
            else 0
        )

        return {
            "ltq_avg_2m": avg_ltq_2m,
            "ltq_avg_5m": avg_ltq_5m,
            "ltq_ratio_2m_5m": ltq_ratio,

            "etq_5m": etq_5m,
            "etq_20m": etq_20m,
            "etq_ratio_5m_20m": etq_ratio,

            "bid_ask_ratio": bid_ask_ratio,

            "smma_distance_pct": smma_distance_pct,

            "price_vs_avg20": price_vs_avg20,
            "price_vs_avg60": price_vs_avg60,

            "signal_direction": (
                1 if signal == "BUY" else -1
            ),
        }