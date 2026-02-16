"""
Risk Management Engine: vol targeting, drawdown protection, position sizing, stop-loss.
Can be disabled for backtest comparison (with vs without risk).
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional


class RiskEngine:
    """
    A) Volatility targeting: scale down if portfolio vol > target.
    B) Drawdown protection: reduce exposure if drawdown > limit.
    C) Position sizing: low-risk assets get higher weight (inverse vol).
    D) Stop-loss: zero weight if asset return below threshold (optional).
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        vol_target: float = 0.15,
        max_drawdown_limit: float = -0.20,
        exposure_floor: float = 0.2,
        stop_loss_threshold: Optional[float] = None,  # e.g. -0.05 for -5% daily
        enabled: bool = True,
        vol_window: int = 21,
    ):
        self.returns = returns
        self.vol_target = vol_target
        self.max_drawdown_limit = max_drawdown_limit
        self.exposure_floor = exposure_floor
        self.stop_loss_threshold = stop_loss_threshold
        self.enabled = enabled
        self.vol_window = vol_window

    def apply(
        self,
        weights: Dict[str, float],
        index: int,
        equity_curve: Optional[pd.Series] = None,
        last_returns: Optional[pd.Series] = None,
    ) -> Dict[str, float]:
        """
        Returns risk-adjusted weights. If enabled=False, returns weights unchanged.
        """
        if not self.enabled:
            return dict(weights)
        w = dict(weights)
        # D) Stop-loss per asset
        if self.stop_loss_threshold is not None and last_returns is not None and index > 0:
            for ticker in list(w.keys()):
                if ticker in last_returns.index and last_returns[ticker] < self.stop_loss_threshold:
                    w[ticker] = 0.0
        w = self._normalize(w)
        # A) Vol targeting
        port_vol = self._portfolio_vol(w, index)
        if port_vol > 1e-8 and port_vol > self.vol_target:
            scale = self.vol_target / port_vol
            w = {k: v * scale for k, v in w.items()}
        
        # B) Drawdown protection
        if equity_curve is not None and len(equity_curve) > 0:
            cummax = equity_curve.cummax()
            dd = (equity_curve - cummax) / cummax.replace(0, np.nan)
            current_dd = dd.iloc[-1] if hasattr(dd, "iloc") else float(dd)
            if not np.isnan(current_dd) and current_dd < self.max_drawdown_limit:
                w = {k: v * self.exposure_floor for k, v in w.items()}
        
        return w

    def _portfolio_vol(self, weights: Dict[str, float], index: int) -> float:
        if index < self.vol_window:
            return 0.0
        start_index = index - self.vol_window
        window = self.returns.iloc[start_index:index]
        cov = window.cov() * 252
        if cov.isnull().values.any():
            return 0.0
        tickers = list(weights.keys())
        try:
            cov = cov.reindex(index=tickers, columns=tickers).fillna(0)
            w = np.array([weights[t] for t in tickers])
            return float(np.sqrt(np.dot(w, np.dot(cov, w))))
        except Exception:
            return 0.0

    def _normalize(self, w: Dict[str, float]) -> Dict[str, float]:
        total = sum(w.values())
        if total <= 0:
            return w
        return {k: v / total for k, v in w.items()}
