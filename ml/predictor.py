import os

import joblib
import pandas as pd


FEATURES = [
    "ltq_avg_2m",
    "ltq_avg_5m",
    "ltq_ratio_2m_5m",
    "etq_5m",
    "etq_20m",
    "etq_ratio_5m_20m",
    "bid_ask_ratio",
    "smma_distance_pct",
    "price_vs_avg20",
    "price_vs_avg60",
    "signal_direction",
]


class CrossoverPredictor:

    def __init__(
        self,
        model_path="models/crossover_model.pkl",
        threshold=0.60,
    ):
        self.threshold = threshold
        self.model = None

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)

    def predict(self, features):

        if self.model is None or features is None:
            return None

        X = pd.DataFrame(
            [[features[name] for name in FEATURES]],
            columns=FEATURES,
        )

        probability = self.model.predict_proba(X)[0][1]

        decision = (
            "ACCEPT"
            if probability >= self.threshold
            else "AVOID"
        )

        reasons = self._build_reasons(
            features,
            decision,
        )

        return {
            "probability": float(probability),
            "confidence_pct": round(
                probability * 100,
                2,
            ),
            "decision": decision,
            "reasons": reasons,
        }

    def _build_reasons(self, features, decision):

        observations = []

        signal = (
            "BUY"
            if features["signal_direction"] == 1
            else "SELL"
        )

        ltq_ratio = features["ltq_ratio_2m_5m"]
        bid_ask = features["bid_ask_ratio"]
        price20 = features["price_vs_avg20"]
        smma_distance = features["smma_distance_pct"]

        # LTQ momentum
        if ltq_ratio > 1.10:
            observations.append(
                "Recent LTQ is elevated relative to "
                "the 5-minute average."
            )

        elif ltq_ratio < 0.90:
            observations.append(
                "Recent LTQ activity is weakening."
            )

        else:
            observations.append(
                "Recent LTQ activity is relatively stable."
            )

        # Order-book pressure
        if signal == "BUY":

            if bid_ask > 1.10:
                observations.append(
                    "Bid-side liquidity supports the BUY signal."
                )

            elif bid_ask < 0.90:
                observations.append(
                    "Ask-side liquidity creates pressure "
                    "against the BUY signal."
                )

        else:

            if bid_ask < 0.90:
                observations.append(
                    "Ask-side liquidity supports the SELL signal."
                )

            elif bid_ask > 1.10:
                observations.append(
                    "Bid-side liquidity creates pressure "
                    "against the SELL signal."
                )

        # Price position
        if signal == "BUY":

            if price20 > 0:
                observations.append(
                    "Price is above its 20-minute average, "
                    "supporting upward momentum."
                )
            else:
                observations.append(
                    "Price remains below its 20-minute average."
                )

        else:

            if price20 < 0:
                observations.append(
                    "Price is below its 20-minute average, "
                    "supporting downward momentum."
                )
            else:
                observations.append(
                    "Price remains above its 20-minute average."
                )

        # Crossover strength
        if abs(smma_distance) < 0.01:
            observations.append(
                "SMMA separation is small, indicating "
                "a relatively weak crossover."
            )

        # Explicit model statement
        if decision == "ACCEPT":
            observations.insert(
                0,
                "The ML model classified this crossover "
                "above the acceptance threshold."
            )
        else:
            observations.insert(
                0,
                "The ML model classified this crossover "
                "below the acceptance threshold."
            )

        return observations