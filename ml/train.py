import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


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


def train_model(
    dataset_path="data/crossover_dataset.csv",
    model_path="models/crossover_model.pkl",
):

    df = pd.read_csv(dataset_path)

    print(f"Samples: {len(df)}")
    print("\nLabels:")
    print(df["profitable"].value_counts())

    # Basic validation
    if len(df) < 20:
        raise ValueError(
            "Not enough samples. Need at least 20 for testing."
        )

    if df["profitable"].nunique() < 2:
        raise ValueError(
            "Dataset must contain both profitable and losing trades."
        )

    X = df[FEATURES]
    y = df["profitable"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nModel Evaluation")
    print(classification_report(y_test, predictions))

    os.makedirs(
        os.path.dirname(model_path),
        exist_ok=True,
    )

    joblib.dump(model, model_path)

    print(f"\nModel saved: {model_path}")


if __name__ == "__main__":
    train_model()