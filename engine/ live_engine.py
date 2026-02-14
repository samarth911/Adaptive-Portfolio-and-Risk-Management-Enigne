# engine/live_engine.py

import time
from engine.portfolio_state import PortfolioState
from regime.regime_detector import RegimeDetector
from allocation.risk_parity import RiskParityAllocator
from risk.risk_engine import RiskEngine


class AutonomousEngine:

    def __init__(self, prices_df):

        self.prices = prices_df
        self.state = PortfolioState()
        self.regime_detector = RegimeDetector(prices_df)
        self.allocator = RiskParityAllocator(prices_df)
        self.risk_engine = RiskEngine(prices_df.pct_change().dropna())
        self.running = False

    def start(self):
        self.running = True
        print("Engine started...")

        for i in range(60, len(self.prices)):

            if not self.running:
                break

            regime = self.regime_detector.detect_regime(i)
            self.state.current_regime = regime

            weights = self.allocator.allocate()

            weights = self.risk_engine.apply_risk_controls(
                weights,
                self.state.history,
                i
            )

            prices_today = self.prices.iloc[i].to_dict()

            self.state.update_positions(weights, prices_today)
            self.state.update_value(prices_today)

            time.sleep(0.2)  # simulate daily step

        print("Engine finished.")

    def stop(self):
        self.running = False

    def get_state(self):
        return self.state.get_snapshot()
