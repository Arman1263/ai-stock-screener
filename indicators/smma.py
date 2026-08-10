class SMMA:

    def __init__(self, period):
        self.period = period
        self.value = None
        self.prices = []

    def update(self, price):
        # Collect enough prices for initial SMMA
        if self.value is None:
            self.prices.append(price)

            if len(self.prices) < self.period:
                return None

            self.value = sum(self.prices) / self.period
            return self.value

        # SMMA formula
        self.value = (
            (self.value * (self.period - 1)) + price
        ) / self.period

        return self.value   