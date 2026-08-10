from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def generate_ticks(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass