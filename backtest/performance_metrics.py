# backtest/performance_metrics.py

import pandas as pd
import numpy as np


class PerformanceMetrics:
    """
    Computes portfolio performance statistics.
    """

    def __init__(self, equity_curve: pd.Series, risk_free_rate: float = 0.02):
        self.equity_curve = equity_curve
        self.risk_free_rate = risk_free_rate
        self.returns = self._compute_returns()

    # -------------------------------------------------------
    # 1️⃣ Daily Returns from Equity Curve
    # -------------------------------------------------------
    def _compute_returns(self):
        return self.equity_curve.pct_change().dropna()

    # -------------------------------------------------------
    # 2️⃣ CAGR
    # -------------------------------------------------------
    def cagr(self):
        years = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days / 365.25
        total_return = self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]
        return total_return ** (1 / years) - 1

    # -------------------------------------------------------
    # 3️⃣ Volatility (Annualized)
    # -------------------------------------------------------
    def annual_volatility(self):
        return self.returns.std() * np.sqrt(252)

    # -------------------------------------------------------
    # 4️⃣ Sharpe Ratio
    # -------------------------------------------------------
    def sharpe_ratio(self):
        excess_return = self.returns.mean() * 252 - self.risk_free_rate
        vol = self.annual_volatility()
        return excess_return / vol if vol != 0 else 0

    # -------------------------------------------------------
    # 5️⃣ Sortino Ratio
    # -------------------------------------------------------
    def sortino_ratio(self):
        downside = self.returns[self.returns < 0]
        downside_std = downside.std() * np.sqrt(252)
        excess_return = self.returns.mean() * 252 - self.risk_free_rate
        return excess_return / downside_std if downside_std != 0 else 0

    # -------------------------------------------------------
    # 6️⃣ Max Drawdown
    # -------------------------------------------------------
    def max_drawdown(self):
        cumulative_max = self.equity_curve.cummax()
        drawdown = (self.equity_curve - cumulative_max) / cumulative_max
        return drawdown.min()

    # -------------------------------------------------------
    # 7️⃣ Calmar Ratio
    # -------------------------------------------------------
    def calmar_ratio(self):
        max_dd = abs(self.max_drawdown())
        return self.cagr() / max_dd if max_dd != 0 else 0

    # -------------------------------------------------------
    # 8️⃣ Summary Report
    # -------------------------------------------------------
    def summary(self):
        return {
            "CAGR": self.cagr(),
            "Annual Volatility": self.annual_volatility(),
            "Sharpe Ratio": self.sharpe_ratio(),
            "Sortino Ratio": self.sortino_ratio(),
            "Max Drawdown": self.max_drawdown(),
            "Calmar Ratio": self.calmar_ratio()
        }

