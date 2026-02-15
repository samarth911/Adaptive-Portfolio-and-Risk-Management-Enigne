"""
Allocation Engine: regime-adaptive dynamic allocation.
Methods: Risk Parity, Momentum, Correlation-aware, regime-based templates.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from ..regime_engine.detector import (
    REGIME_CRASH,
    REGIME_HIGH_VOL,
    REGIME_TRENDING_UP,
    REGIME_TRENDING_DOWN,
)


class AllocationEngine:
    """
    Produces portfolio weights from regime + optional features.
    Supports risk parity, momentum, and regime-based defensive shifts.
    """

    def __init__(self, tickers: List[str]):
        self.tickers = list(tickers)

    def get_weights(
        self,
        regime: str,
        returns: Optional[pd.DataFrame] = None,
        cov_matrix: Optional[pd.DataFrame] = None,
        momentum_scores: Optional[pd.Series] = None,
        method: str = "regime",  # "regime" | "risk_parity" | "momentum" | "equal"
    ) -> Dict[str, float]:
        """
        Returns normalized weights dict. If method is 'regime', uses regime templates.
        Otherwise uses quantitative method then optionally tilts by regime.
        """
        n = len(self.tickers)
        if method == "risk_parity" and cov_matrix is not None:
            w = self._risk_parity_weights(cov_matrix)
        elif method == "momentum" and momentum_scores is not None:
            w = self._momentum_weights(momentum_scores)
        elif method == "equal":
            w = {t: 1.0 / n for t in self.tickers}
        else:
            w = self._regime_weights(regime)
        return self._normalize(w)

    def _regime_weights(self, regime: str) -> Dict[str, float]:
        """Regime-based templates (equity = first ticker, bond = second)."""
        n = len(self.tickers)
        if regime == REGIME_TRENDING_UP:
            w = {self.tickers[0]: 0.7}
            rest = 0.3 / (n - 1) if n > 1 else 0
            for t in self.tickers[1:]:
                w[t] = rest
            return w
        if regime == REGIME_TRENDING_DOWN:
            w = {}
            bond_w = 0.6 if n >= 2 else 1.0
            eq_w = 0.4 / max(1, n - 1) if n > 1 else 0
            for i, t in enumerate(self.tickers):
                w[t] = bond_w if i == 1 else eq_w
            if n == 1:
                w[self.tickers[0]] = 1.0
            return w
        if regime == REGIME_HIGH_VOL:
            return {t: 1.0 / n for t in self.tickers}
        if regime == REGIME_CRASH:
            w = {}
            for i, t in enumerate(self.tickers):
                w[t] = 0.8 if i == 1 else 0.2 / max(1, n - 1)
            if n == 1:
                w[self.tickers[0]] = 1.0
            return w
        return {t: 1.0 / n for t in self.tickers}

    def _risk_parity_weights(self, cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Inverse-volatility risk parity."""
        try:
            vols = np.sqrt(np.diag(cov_matrix))
            vols = np.where(vols <= 0, 1e-8, vols)
            inv_vol = 1.0 / vols
            w = inv_vol / inv_vol.sum()
            return dict(zip(self.tickers, w))
        except Exception:
            return {t: 1.0 / len(self.tickers) for t in self.tickers}

    def _momentum_weights(self, momentum_scores: pd.Series) -> Dict[str, float]:
        """Weights proportional to positive momentum."""
        aligned = momentum_scores.reindex(self.tickers).fillna(0)
        positive = aligned.clip(lower=0)
        if positive.sum() <= 0:
            return {t: 1.0 / len(self.tickers) for t in self.tickers}
        w = (positive / positive.sum()).to_dict()
        return w

    def _normalize(self, w: Dict[str, float]) -> Dict[str, float]:
        total = sum(w.values())
        if total <= 0:
            return {t: 1.0 / len(self.tickers) for t in self.tickers}
        return {k: v / total for k, v in w.items()}
