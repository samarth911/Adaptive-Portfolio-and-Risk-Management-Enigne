# regime/regime_detector.py

import pandas as pd


class RegimeDetector:
    """
    Detects market regime using rule-based logic.

    Possible regimes:
    - BULL
    - BEAR
    - HIGH_VOL
    - CRISIS
    """

    def __init__(
        self,
        volatility: pd.DataFrame,
        drawdown: pd.DataFrame,
        trend_signal: pd.DataFrame,
        vol_threshold: float = 0.25,
        drawdown_threshold: float = -0.15
    ):
        self.volatility = volatility
        self.drawdown = drawdown
        self.trend_signal = trend_signal
        self.vol_threshold = vol_threshold
        self.drawdown_threshold = drawdown_threshold

    # -------------------------------------------------------
    # 1️⃣ Detect Regime for Single Date Index
    # -------------------------------------------------------
    def detect(self, date_index: int) -> str:

        current_vol = self.volatility.iloc[date_index].mean()
        current_dd = self.drawdown.iloc[date_index].mean()
        trend = self.trend_signal.iloc[date_index].mean()

        # CRISIS regime
        if current_dd < self.drawdown_threshold:
            return "CRISIS"

        # HIGH VOL regime
        if current_vol > self.vol_threshold:
            return "HIGH_VOL"

        # BULL regime
        if trend > 0.5:
            return "BULL"

        # Default
        return "BEAR"

    # -------------------------------------------------------
    # 2️⃣ Generate Full Regime Series
    # -------------------------------------------------------
    def generate_regime_series(self) -> pd.Series:

        regimes = []

        for i in range(len(self.volatility)):
            regime = self.detect(i)
            regimes.append(regime)

        regime_series = pd.Series(
            regimes,
            index=self.volatility.index
        )

        return regime_series
