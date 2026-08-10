class CrossoverDetector:

    def __init__(self):
        self.previous_smma20 = None
        self.previous_smma120 = None

    def detect(self, smma20, smma120):

        if smma20 is None or smma120 is None:
            return None

        signal = None

        if (
            self.previous_smma20 is not None
            and self.previous_smma120 is not None
        ):
            # BUY crossover
            if (
                self.previous_smma20 <= self.previous_smma120
                and smma20 > smma120
            ):
                signal = "BUY"

            # SELL crossover
            elif (
                self.previous_smma20 >= self.previous_smma120
                and smma20 < smma120
            ):
                signal = "SELL"

        self.previous_smma20 = smma20
        self.previous_smma120 = smma120

        return signal