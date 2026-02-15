"""
Regime Detection Engine: two approaches.
1) Rule-based: volatility + drawdown thresholds + trend.
2) Clustering: KMeans on vol, drawdown, trend features.
Output: TRENDING_UP | TRENDING_DOWN | HIGH_VOL | CRASH
"""

import pandas as pd
import numpy as np
from typing import Optional

# Optional sklearn for clustering
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


REGIME_TRENDING_UP = "TRENDING_UP"
REGIME_TRENDING_DOWN = "TRENDING_DOWN"
REGIME_HIGH_VOL = "HIGH_VOL"
REGIME_CRASH = "CRASH"


class RegimeEngine:
    """
    Detects market regime using rule-based and optional clustering.
    """

    def __init__(
        self,
        vol_threshold: float = 0.25,
        drawdown_threshold: float = -0.15,
        method: str = "rule",  # "rule" | "clustering"
    ):
        self.vol_threshold = vol_threshold
        self.drawdown_threshold = drawdown_threshold
        self.method = method
        self._scaler = StandardScaler() if HAS_SKLEARN else None
        self._kmeans: Optional[KMeans] = None

    def _detect_rule(self, i: int) -> str:
        vol = self.volatility.iloc[i]
        dd = self.drawdown.iloc[i]
        trend = self.trend_signal.iloc[i]
        vol_mean = vol.mean() if hasattr(vol, "mean") else float(vol)
        dd_mean = dd.mean() if hasattr(dd, "mean") else float(dd)
        trend_mean = trend.mean() if hasattr(trend, "mean") else float(trend)
        if dd_mean < self.drawdown_threshold:
            return REGIME_CRASH
        if vol_mean > self.vol_threshold:
            return REGIME_HIGH_VOL
        if trend_mean > 0.5:
            return REGIME_TRENDING_UP
        return REGIME_TRENDING_DOWN

    def _fit_clustering(self, feature_matrix: np.ndarray) -> None:
        if not HAS_SKLEARN:
            return
        self._scaler = StandardScaler()
        X = self._scaler.fit_transform(feature_matrix)
        self._kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        self._kmeans.fit(X)

    def _map_cluster_to_regime(self, label: int, feature_row: np.ndarray) -> str:
        """Map cluster to regime by convention: high vol -> HIGH_VOL, low trend -> DOWN, etc."""
        vol, dd, trend = feature_row[0], feature_row[1], feature_row[2]
        if dd < self.drawdown_threshold:
            return REGIME_CRASH
        if vol > self.vol_threshold:
            return REGIME_HIGH_VOL
        return REGIME_TRENDING_UP if trend > 0.5 else REGIME_TRENDING_DOWN

    def generate_regime_series(
        self,
        volatility: pd.DataFrame,
        drawdown: pd.DataFrame,
        trend_signal: pd.DataFrame,
    ) -> pd.Series:
        """
        Returns a Series of regime labels (TRENDING_UP, TRENDING_DOWN, HIGH_VOL, CRASH)
        aligned to the same index as volatility.
        """
        self.volatility = volatility
        self.drawdown = drawdown
        self.trend_signal = trend_signal
        n = len(volatility)
        regimes = []
        if self.method == "clustering" and HAS_SKLEARN:
            vol_flat = volatility.mean(axis=1).values.reshape(-1, 1)
            dd_flat = drawdown.mean(axis=1).values.reshape(-1, 1)
            trend_flat = trend_signal.mean(axis=1).values.reshape(-1, 1)
            feature_matrix = np.hstack([vol_flat, dd_flat, trend_flat])
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
            self._fit_clustering(feature_matrix)
            X = self._scaler.transform(feature_matrix)
            labels = self._kmeans.predict(X)
            for i in range(n):
                regimes.append(self._map_cluster_to_regime(labels[i], feature_matrix[i]))
        else:
            for i in range(n):
                regimes.append(self._detect_rule(i))
        return pd.Series(regimes, index=volatility.index)
