# main_engine.py

from data.data_loader import DataLoader
from features.feature_engine import FeatureEngine
from regime.regime_detector import RegimeDetector
from allocation.base_allocator import BaseAllocator
from risk.risk_engine import RiskEngine
from backtest.backtester import Backtester
from backtest.performance_metrics import PerformanceMetrics
from explainability.decision_logger import DecisionLogger

import pandas as pd


class AutonomousPortfolioEngine:

    def __init__(
        self,
        tickers,
        start_date,
        end_date
    ):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

        # Core objects (initialized later)
        self.loader = None
        self.features = None
        self.regime_series = None
        self.allocator = None
        self.risk_engine = None
        self.logger = DecisionLogger()

    # -------------------------------------------------------
    # 1️⃣ Data Layer
    # -------------------------------------------------------
    def load_data(self):
        self.loader = DataLoader(
            tickers=self.tickers,
            start_date=self.start_date,
            end_date=self.end_date
        )

        prices = self.loader.download_data()
        returns = self.loader.compute_returns()

        return prices, returns

    # -------------------------------------------------------
    # 2️⃣ Feature Layer
    # -------------------------------------------------------
    def generate_features(self, prices):

        fe = FeatureEngine(prices)
        feature_set = fe.generate_all_features()

        self.features = feature_set
        return feature_set

    # -------------------------------------------------------
    # 3️⃣ Regime Detection
    # -------------------------------------------------------
    def detect_regime(self):

        detector = RegimeDetector(
            volatility=self.features["volatility"],
            drawdown=self.features["drawdown"],
            trend_signal=self.features["trend_signal"]
        )

        self.regime_series = detector.generate_regime_series()
        return self.regime_series

    # -------------------------------------------------------
    # 4️⃣ Allocation + Risk Wrapper
    # -------------------------------------------------------
    def build_allocation_function(self, returns):

        self.allocator = BaseAllocator(self.tickers)
        self.risk_engine = RiskEngine(returns)

        equity_curve_tracker = pd.Series(index=returns.index, dtype=float)

        def allocation_function(i):

            regime = self.regime_series.iloc[i]
            base_weights = self.allocator.get_weights(regime)

            # Apply risk controls
            adjusted_weights = self.risk_engine.apply_risk_controls(
                weights=base_weights,
                index=i,
                equity_curve=equity_curve_tracker[:i] if i > 0 else None
            )

            return adjusted_weights

        return allocation_function

    # -------------------------------------------------------
    # 5️⃣ Run Full Backtest
    # -------------------------------------------------------
    def run(self):

        # Load data
        prices, returns = self.load_data()

        # Features
        self.generate_features(prices)

        # Regime
        self.detect_regime()

        # Allocation Function
        allocation_function = self.build_allocation_function(returns)

        # Backtest
        backtester = Backtester(
            returns=returns,
            allocation_function=allocation_function
        )

        equity_curve = backtester.run()

        # Metrics
        metrics = PerformanceMetrics(equity_curve)
        report = metrics.summary()

        return {
            "equity_curve": equity_curve,
            "metrics": report,
            "regime_series": self.regime_series
        }
