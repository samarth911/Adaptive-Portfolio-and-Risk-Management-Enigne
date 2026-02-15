# risk/risk_engine.py

import numpy as np
import pandas as pd
from typing import Dict


class RiskEngine:
    """
    Applies multiple risk controls:
    - Volatility targeting
    - Drawdown protection
    - Exposure scaling
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        vol_target: float = 0.15,          # 15% annual vol target
        max_drawdown_limit: float = -0.20, # 20% drawdown cutoff
        exposure_floor: float = 0.2        # minimum exposure level
    ):
        self.returns = returns
        self.vol_target = vol_target
        self.max_drawdown_limit = max_drawdown_limit
        self.exposure_floor = exposure_floor

    # -------------------------------------------------------
    # 1️⃣ Portfolio Volatility
    # -------------------------------------------------------
    def compute_portfolio_vol(self, weights: Dict[str, float], index: int):

        # Not enough data → skip vol targeting
        if index < 30:
            return 0

        window_returns = self.returns.iloc[:index]

        cov_matrix = window_returns.cov() * 252

        # If covariance contains NaN → skip
        if cov_matrix.isnull().values.any():
            return 0

        weight_vector = np.array(list(weights.values()))

        port_vol = np.sqrt(
            np.dot(weight_vector.T, np.dot(cov_matrix, weight_vector))
        )

        return port_vol


    # -------------------------------------------------------
    # 2️⃣ Portfolio Drawdown
    # -------------------------------------------------------
    def compute_drawdown(self, equity_curve: pd.Series):
        cumulative_max = equity_curve.cummax()
        drawdown = (equity_curve - cumulative_max) / cumulative_max
        return drawdown.iloc[-1]

    # -------------------------------------------------------
    # 3️⃣ Apply Risk Controls
    # -------------------------------------------------------
    def apply_risk_controls(
        self,
        weights: Dict[str, float],
        index: int,
        equity_curve: pd.Series = None
    ) -> Dict[str, float]:

        adjusted_weights = weights.copy()

        # ---- Volatility Targeting ----
        port_vol = self.compute_portfolio_vol(weights, index)

        if port_vol > self.vol_target:
            scale_factor = self.vol_target / port_vol
            adjusted_weights = {
                k: v * scale_factor for k, v in adjusted_weights.items()
            }

        # ---- Drawdown Protection ----
        if equity_curve is not None:
            current_dd = self.compute_drawdown(equity_curve)

            if current_dd < self.max_drawdown_limit:
                adjusted_weights = {
                    k: v * self.exposure_floor for k, v in adjusted_weights.items()
                }

        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {
                k: v / total_weight for k, v in adjusted_weights.items()
            }

        return adjusted_weights
