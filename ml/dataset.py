import csv
import os


class DatasetBuilder:

    def __init__(self, filepath="data/crossover_dataset.csv"):
        self.filepath = filepath
        self.pending_features = {}

        os.makedirs(
            os.path.dirname(filepath),
            exist_ok=True
        )

    def register_crossover(self, symbol, features):
        self.pending_features[symbol] = features

    def complete_trade(self, symbol, trade):

        features = self.pending_features.get(symbol)

        if features is None:
            return

        row = {
            "symbol": symbol,
            **features,
            "pnl": trade["pnl"],
            "profitable": int(trade["profitable"]),
        }

        file_exists = os.path.exists(self.filepath)

        with open(
            self.filepath,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=row.keys()
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        del self.pending_features[symbol]