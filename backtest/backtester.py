# backtest/backtester.py

import pandas as pd
import numpy as np
from typing import Callable, Dict


class Backtester:
    """
    Simulates portfolio performance using:
    - Dynamic allocation function
    - Risk-adjusted weights
    - Rebalancing logic
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        allocation_function: Callable,
        rebalance_frequency: int = 21,  # monthly (~21 trading days)
        transaction_cost: float = 0.0005  # 5 bps
    ):
        """
        returns: daily log returns DataFrame
        allocation_function: function(date_index) -> weight dict
        """
        self.returns = returns
        self.allocation_function = allocation_function
        self.rebalance_frequency = rebalance_frequency
        self.transaction_cost = transaction_cost

        self.portfolio_value = None
        self.weights_history = []

    # -------------------------------------------------------
    # 1️⃣ Run Backtest
    # -------------------------------------------------------
    def run(self, initial_capital: float = 1_000_000) -> pd.Series:

        dates = self.returns.index
        portfolio_value = pd.Series(index=dates, dtype=float)
        portfolio_value.iloc[0] = initial_capital

        current_weights = None
        previous_weights = pd.Series(0, index=self.returns.columns)

        for i in range(1, len(dates)):

            # -----------------------------
            # Rebalance logic
            # -----------------------------
            if i % self.rebalance_frequency == 0 or current_weights is None:

                raw_weights = self.allocation_function(i)

                # Convert dict → aligned Series
                current_weights = pd.Series(raw_weights)
                current_weights = current_weights.reindex(self.returns.columns).fillna(0)

                self.weights_history.append((dates[i], current_weights.copy()))

                # Transaction cost based on turnover
                turnover = np.abs(current_weights - previous_weights).sum()
                cost = self.transaction_cost * turnover

                previous_weights = current_weights.copy()

            else:
                cost = 0

            # -----------------------------
            # Portfolio Return
            # -----------------------------
            daily_return = (current_weights * self.returns.iloc[i]).sum()

            portfolio_value.iloc[i] = (
                portfolio_value.iloc[i - 1] *
                (1 + daily_return - cost)
            )

        self.portfolio_value = portfolio_value
        return portfolio_value


    # -------------------------------------------------------
    # 2️⃣ Get Weights History
    # -------------------------------------------------------
    def get_weights_history(self):
        return self.weights_history
