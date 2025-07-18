from collections import deque

class PriceBuffer:
    def __init__(self, maxlen=100):
        self.prices = deque(maxlen=maxlen)

    def add_price(self, price):
        self.prices.append(price)

    def get_prices(self):
        return list(self.prices)
