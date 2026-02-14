import yfinance as yf
import threading
import time
from datetime import datetime
import numpy as np

class RealTimePortfolioEngine:

    def __init__(self, tickers, capital=100000):

        self.tickers = tickers
        self.capital = capital
        self.cash = capital
        self.positions = {t: 0 for t in tickers}
        self.history = []
        self.logs = []
        self.regime = "UNKNOWN"
        self.running = False

    def log(self, message):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message
        })

    def fetch_prices(self):
        data = yf.download(self.tickers, period="1d", interval="1m")
        latest = data["Close"].iloc[-1]
        return latest.to_dict()

    def detect_regime(self, prices):
        vol = np.std(list(prices.values()))
        if vol > 5:
            return "HIGH VOLATILITY"
        return "STABLE"

    def allocate(self, prices):
        weight = 1 / len(self.tickers)
        allocation = {}

        for t in self.tickers:
            allocation[t] = weight

        return allocation

    def rebalance(self, prices):
        weights = self.allocate(prices)

        for t in self.tickers:
            allocation_value = self.capital * weights[t]
            self.positions[t] = allocation_value / prices[t]

        self.log("Portfolio rebalanced")

    def update_value(self, prices):
        total = 0
        for t in self.tickers:
            total += self.positions[t] * prices[t]
        self.capital = total
        self.history.append(total)

    def run(self):

        self.running = True
        self.log("Engine started")

        while self.running:

            prices = self.fetch_prices()

            self.regime = self.detect_regime(prices)
            self.log(f"Regime detected: {self.regime}")

            self.rebalance(prices)
            self.update_value(prices)

            time.sleep(10)  # update every 10 seconds

    def start(self):
        if not self.running:
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()


    def stop(self):
        self.running = False
        self.log("Engine stopped")

    def add_fund(self, ticker):
        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self.positions[ticker] = 0
            self.log(f"Added new fund: {ticker}")

    def get_state(self):

        total_value = self.capital if self.capital > 0 else 1

        allocation_percent = {}

        for t in self.tickers:
            price = self.positions.get(t, 0)
            allocation_percent[t] = float(price)

        return {
            "value": float(self.capital),
            "regime": self.regime,
            "allocations": allocation_percent,
            "history": self.history,
            "logs": self.logs
        }

