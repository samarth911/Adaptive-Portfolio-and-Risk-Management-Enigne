"""
Regime Detection Engine: Clustering using KMeans on vol, drawdown, trend features.
Output: TRENDING_UP | TRENDING_DOWN | HIGH_VOL | CRASH
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


REGIME_TRENDING_UP = "TRENDING_UP"
REGIME_TRENDING_DOWN = "TRENDING_DOWN"
REGIME_HIGH_VOL = "HIGH_VOL"
REGIME_CRASH = "CRASH"


class RegimeEngine:
    """
    Detects market regime using KMeans clustering.
    """

    def __init__(
        self,
        vol_threshold: float = 0.25,
        drawdown_threshold: float = -0.15,
    ):
        self.vol_threshold = vol_threshold
        self.drawdown_threshold = drawdown_threshold
        self._scaler = StandardScaler()
        self._kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)

    def _fit_clustering(self, feature_matrix: np.ndarray) -> None:
        X = self._scaler.fit_transform(feature_matrix)
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

        vol_flat = volatility.mean(axis=1).values.reshape(-1, 1)
        dd_flat = drawdown.mean(axis=1).values.reshape(-1, 1)
        trend_flat = trend_signal.mean(axis=1).values.reshape(-1, 1)
        feature_matrix = np.hstack([vol_flat, dd_flat, trend_flat])
        feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)

        self._fit_clustering(feature_matrix)
        X = self._scaler.transform(feature_matrix)
        labels = self._kmeans.predict(X)

        regimes = [self._map_cluster_to_regime(labels[i], feature_matrix[i]) for i in range(n)]
        return pd.Series(regimes, index=volatility.index)
