"""
Backtest Engine: run with or without risk engine; walk-forward optional.
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Optional, Tuple

from .metrics import backtest_metrics, flag_suspicious


class BacktestEngine:
    """
    Simulates portfolio over returns using an allocation function.
    allocation_function(i, equity_curve_so_far) -> dict of weights.
    equity_curve_so_far is Series of portfolio value up to (not including) day i.
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        allocation_function: Callable,  # (i, equity_curve_so_far) -> dict
        rebalance_frequency: int = 21,
        transaction_cost: float = 0.0005,
        initial_capital: float = 1_000_000,
    ):
        self.returns = returns
        self.allocation_function = allocation_function
        self.rebalance_frequency = rebalance_frequency
        self.transaction_cost = transaction_cost
        self.initial_capital = initial_capital
        self.weights_history: List[Tuple[pd.Timestamp, pd.Series]] = []

    def run(self) -> pd.Series:
        """Returns equity curve (Series)."""
        dates = self.returns.index
        portfolio_value = pd.Series(index=dates, dtype=float)
        portfolio_value.iloc[0] = self.initial_capital
        current_weights = None
        previous_weights = pd.Series(0.0, index=self.returns.columns)

        for i in range(1, len(dates)):
            equity_so_far = portfolio_value.iloc[:i]
            if i % self.rebalance_frequency == 0 or current_weights is None:
                raw = self.allocation_function(i, equity_so_far)
                current_weights = pd.Series(raw).reindex(self.returns.columns).fillna(0)
                self.weights_history.append((dates[i], current_weights.copy()))
                turnover = (current_weights - previous_weights).abs().sum()
                cost = self.transaction_cost * turnover
                previous_weights = current_weights.copy()
            else:
                cost = 0
            daily_ret = (current_weights * self.returns.iloc[i]).sum()
            portfolio_value.iloc[i] = portfolio_value.iloc[i - 1] * (1 + daily_ret - cost)
        return portfolio_value


def run_backtest_with_and_without_risk(
    returns: pd.DataFrame,
    allocation_fn_with_risk: Callable,
    allocation_fn_no_risk: Callable,
    rebalance_frequency: int = 21,
    transaction_cost: float = 0.0005,
    initial_capital: float = 1_000_000,
) -> Tuple[pd.Series, pd.Series, Dict, Dict]:
    """
    Run two backtests (with risk engine, without). Return (equity_with, equity_without, metrics_with, metrics_without).
    Allocation functions must have signature (i, equity_curve_so_far).
    """
    bt_with = BacktestEngine(returns, allocation_fn_with_risk, rebalance_frequency, transaction_cost, initial_capital)
    bt_no = BacktestEngine(returns, allocation_fn_no_risk, rebalance_frequency, transaction_cost, initial_capital)
    equity_with = bt_with.run()
    equity_no = bt_no.run()
    metrics_with = flag_suspicious(backtest_metrics(equity_with))
    metrics_no = flag_suspicious(backtest_metrics(equity_no))
    return equity_with, equity_no, metrics_with, metrics_no
