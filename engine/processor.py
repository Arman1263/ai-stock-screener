from collections import defaultdict

from storage.tick_store import TickStore
from analysis.rolling_metrics import RollingMetrics
from indicators.smma import SMMA
from analysis.crossover import CrossoverDetector
from analysis.trade_tracker import TradeTracker
from screening.screener import StockScreener
from ml.features import FeatureEngine
from ml.dataset import DatasetBuilder
from ml.predictor import CrossoverPredictor
from analysis.history import MarketHistory


class MarketProcessor:

    def __init__(self):

        self.tick_store = TickStore(
            retention_minutes=60
        )

        self.metrics = RollingMetrics(
            self.tick_store
        )

        self.feature_engine = FeatureEngine(
            self.metrics
        )

        self.screener = StockScreener()

        self.dataset_builder = DatasetBuilder()

        self.predictor = CrossoverPredictor()

        self.history = MarketHistory()

        # ----------------------------------------------------
        # Independent state for every stock
        # ----------------------------------------------------

        self.smma20 = defaultdict(
            lambda: SMMA(20)
        )

        self.smma120 = defaultdict(
            lambda: SMMA(120)
        )

        self.detectors = defaultdict(
            CrossoverDetector
        )

        self.trackers = defaultdict(
            TradeTracker
        )

    # ========================================================
    # PROCESS TICK
    # ========================================================

    def process_tick(self, tick):

        # ----------------------------------------------------
        # Store tick
        # ----------------------------------------------------

        self.tick_store.add_tick(tick)

        # ----------------------------------------------------
        # Screening
        # ----------------------------------------------------

        passes_filter = (
            self.screener.passes_filter(tick)
        )

        # ----------------------------------------------------
        # Indicators
        # ----------------------------------------------------

        value20 = self.smma20[
            tick.symbol
        ].update(tick.ltp)

        value120 = self.smma120[
            tick.symbol
        ].update(tick.ltp)

        # ----------------------------------------------------
        # Crossover detection
        # ----------------------------------------------------

        signal = self.detectors[
            tick.symbol
        ].detect(
            value20,
            value120,
        )

        # ----------------------------------------------------
        # ML features
        # ----------------------------------------------------

        features = None

        if signal:

            features = (
                self.feature_engine.create_features(
                    tick=tick,
                    smma20=value20,
                    smma120=value120,
                    signal=signal,
                )
            )

        # ----------------------------------------------------
        # ML prediction
        # ----------------------------------------------------

        prediction = None

        if features:

            prediction = (
                self.predictor.predict(
                    features
                )
            )

        # ----------------------------------------------------
        # Store signal history
        # ----------------------------------------------------

        if signal:

            self.history.add_signal(
                symbol=tick.symbol,
                timestamp=tick.timestamp,
                price=tick.ltp,
                signal=signal,
                prediction=prediction,
            )

        # ----------------------------------------------------
        # Trade tracking
        # ----------------------------------------------------

        trade_event = None

        if signal:

            # ML controls whether a NEW position
            # is allowed to open.
            allow_entry = (
                prediction is not None
                and prediction["decision"] == "ACCEPT"
            )

            trade_event = self.trackers[
                tick.symbol
            ].process_signal(
                signal=signal,
                price=tick.ltp,
                timestamp=tick.timestamp,
                allow_entry=allow_entry,
            )

            # ------------------------------------------------
            # Register crossover features
            # ------------------------------------------------

            if features:

                self.dataset_builder.register_crossover(
                    symbol=tick.symbol,
                    features=features,
                )

            # ------------------------------------------------
            # Completed trade
            # ------------------------------------------------

            if trade_event:

                event = trade_event["event"]

                if event in (
                    "CLOSE",
                    "CLOSE_AND_OPEN",
                ):

                    closed_trade = (
                        trade_event["closed_trade"]
                    )

                    # ----------------------------------------
                    # Save completed trade for ML dataset
                    # ----------------------------------------

                    self.dataset_builder.complete_trade(
                        symbol=tick.symbol,
                        trade=closed_trade,
                    )

                    # ----------------------------------------
                    # Save completed trade to history
                    # ----------------------------------------

                    self.history.add_trade(
                        symbol=tick.symbol,
                        trade=closed_trade,
                    )

        # ====================================================
        # OUTPUT
        # ====================================================

        return {

            "symbol": tick.symbol,

            "ltp": tick.ltp,

            "ltq": tick.ltq,

            "bid_price": tick.bid_price,

            "bid_quantity": tick.bid_quantity,

            "ask_price": tick.ask_price,

            "ask_quantity": tick.ask_quantity,

            "passes_filter": passes_filter,

            "smma20": value20,

            "smma120": value120,

            "etq_5m": self.metrics.get_etq(
                tick.symbol,
                5,
            ),

            "etq_20m": self.metrics.get_etq(
                tick.symbol,
                20,
            ),

            "etq_60m": self.metrics.get_etq(
                tick.symbol,
                60,
            ),

            "avg_ltp_20m": (
                self.metrics.get_average_ltp(
                    tick.symbol,
                    20,
                )
            ),

            "avg_ltp_60m": (
                self.metrics.get_average_ltp(
                    tick.symbol,
                    60,
                )
            ),

            "signal": signal,

            "features": features,

            "prediction": prediction,

            "trade_event": trade_event,
        }

    # ========================================================
    # HISTORY ACCESS
    # ========================================================

    def get_signal_history(self):

        return self.history.get_signals()

    def get_trade_history(self):

        return self.history.get_trades()