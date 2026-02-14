# engine/portfolio_state.py

class PortfolioState:
    def __init__(self, initial_capital=100000):

        self.initial_capital = initial_capital
        self.current_value = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.history = []
        self.current_regime = "UNKNOWN"

    def update_positions(self, weights, prices):
        self.positions = {}

        for asset, weight in weights.items():
            allocation = self.current_value * weight
            quantity = allocation / prices[asset]
            self.positions[asset] = quantity

    def update_value(self, prices):
        total = 0
        for asset, qty in self.positions.items():
            total += qty * prices[asset]

        self.current_value = total
        self.history.append(total)

    def get_snapshot(self):
        return {
            "value": self.current_value,
            "regime": self.current_regime,
            "positions": self.positions
        }
