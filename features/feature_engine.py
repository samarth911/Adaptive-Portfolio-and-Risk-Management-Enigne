# features/feature_engine.py

import pandas as pd
import numpy as np


class FeatureEngine:
    """
    Generates market features used for:
    - Regime detection
    - Allocation logic
    - Risk adjustments
    """

    def __init__(self, prices: pd.DataFrame):
        self.prices = prices
        self.returns = self._compute_returns()

    # -------------------------------------------------------
    # 1️⃣ Compute Returns
    # -------------------------------------------------------
    def _compute_returns(self):
        return self.prices.pct_change().dropna()

    # -------------------------------------------------------
    # 2️⃣ Rolling Volatility
    # -------------------------------------------------------
    def rolling_volatility(self, window: int = 21):
        return self.returns.rolling(window).std() * np.sqrt(252)

    # -------------------------------------------------------
    # 3️⃣ Rolling Mean Return (Momentum Proxy)
    # -------------------------------------------------------
    def rolling_momentum(self, window: int = 63):
        return self.returns.rolling(window).mean()

    # -------------------------------------------------------
    # 4️⃣ Moving Average Trend
    # -------------------------------------------------------
    def moving_average_trend(self, short_window: int = 50, long_window: int = 200):
        short_ma = self.prices.rolling(short_window).mean()
        long_ma = self.prices.rolling(long_window).mean()
        trend_signal = short_ma > long_ma
        return trend_signal.astype(int)

    # -------------------------------------------------------
    # 5️⃣ Rolling Drawdown
    # -------------------------------------------------------
    def rolling_drawdown(self):
        cumulative_max = self.prices.cummax()
        drawdown = (self.prices - cumulative_max) / cumulative_max
        return drawdown

    # -------------------------------------------------------
    # 6️⃣ Rolling Correlation Matrix
    # -------------------------------------------------------
    def rolling_correlation(self, window: int = 63):
        return self.returns.rolling(window).corr()

    # -------------------------------------------------------
    # 7️⃣ Aggregate Feature Set
    # -------------------------------------------------------
    def generate_all_features(self):
        features = {
            "returns": self.returns,
            "volatility": self.rolling_volatility(),
            "momentum": self.rolling_momentum(),
            "trend_signal": self.moving_average_trend(),
            "drawdown": self.rolling_drawdown(),
            "correlation": self.rolling_correlation()
        }

        return features
