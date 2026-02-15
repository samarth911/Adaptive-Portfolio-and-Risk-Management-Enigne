"""
Stress Test Engine: -5% daily shock, volatility spike, correlation spike.
Evaluates portfolio impact and whether risk engine would protect.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable


class StressTestEngine:
    """
    Apply stress scenarios to returns and optionally re-run allocation/risk to see impact.
    """

    def __init__(self, returns: pd.DataFrame):
        self.returns = returns.copy()

    def apply_daily_shock(
        self,
        shock_pct: float = -0.05,
        num_days: int = 5,
        at_start: bool = True,
    ) -> pd.DataFrame:
        """Apply same daily return shock for num_days (e.g. -5% per day)."""
        stressed = self.returns.copy()
        if at_start:
            for i in range(min(num_days, len(stressed))):
                stressed.iloc[i] = shock_pct
        else:
            # at end
            for i in range(max(0, len(stressed) - num_days), len(stressed)):
                stressed.iloc[i] = shock_pct
        return stressed

    def apply_volatility_spike(
        self,
        multiplier: float = 3.0,
        num_days: int = 10,
        at_start: bool = True,
    ) -> pd.DataFrame:
        """Scale returns by multiplier to simulate vol spike."""
        stressed = self.returns.copy()
        idx = range(min(num_days, len(stressed))) if at_start else range(max(0, len(stressed) - num_days), len(stressed))
        for i in idx:
            stressed.iloc[i] = stressed.iloc[i] * multiplier
        return stressed

    def apply_correlation_spike(
        self,
        num_days: int = 10,
        at_start: bool = True,
    ) -> pd.DataFrame:
        """Force all assets to move together (same return)."""
        stressed = self.returns.copy()
        idx = list(range(min(num_days, len(stressed)))) if at_start else list(range(max(0, len(stressed) - num_days), len(stressed)))
        for i in idx:
            common = stressed.iloc[i].mean()
            for c in stressed.columns:
                stressed.iloc[i][c] = common
        return stressed

    def run_stress_backtest(
        self,
        allocation_function: Callable[[int], Dict[str, float]],
        initial_capital: float = 1_000_000,
        rebalance_frequency: int = 21,
    ) -> Dict[str, float]:
        """
        Run a simple backtest on stressed returns (shock scenario) and return final metrics.
        """
        from ..backtest_engine.runner import BacktestEngine
        from ..backtest_engine.metrics import backtest_metrics
        stressed = self.apply_daily_shock(-0.05, 5)
        bt = BacktestEngine(stressed, allocation_function, rebalance_frequency, 0.0005, initial_capital)
        equity = bt.run()
        return backtest_metrics(equity)
