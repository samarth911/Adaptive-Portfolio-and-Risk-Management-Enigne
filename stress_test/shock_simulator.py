# stress_test/shock_simulator.py

import pandas as pd
import numpy as np


class ShockSimulator:
    """
    Simulates extreme market stress scenarios:
    - Sudden market crash
    - Volatility spike
    - Correlation spike
    """

    def __init__(self, returns: pd.DataFrame):
        self.original_returns = returns.copy()

    # -------------------------------------------------------
    # 1️⃣ Sudden Market Shock
    # -------------------------------------------------------
    def apply_market_shock(
        self,
        shock_size: float = -0.05,   # -5% daily shock
        shock_duration: int = 5      # 5 consecutive days
    ) -> pd.DataFrame:

        stressed_returns = self.original_returns.copy()

        # Apply shock to all assets
        stressed_returns.iloc[:shock_duration] = shock_size

        return stressed_returns

    # -------------------------------------------------------
    # 2️⃣ Volatility Spike Simulation
    # -------------------------------------------------------
    def apply_volatility_spike(
        self,
        spike_multiplier: float = 3.0,
        spike_duration: int = 10
    ) -> pd.DataFrame:

        stressed_returns = self.original_returns.copy()

        noise = np.random.normal(
            0,
            stressed_returns.std() * spike_multiplier,
            size=stressed_returns.iloc[:spike_duration].shape
        )

        stressed_returns.iloc[:spike_duration] += noise

        return stressed_returns

    # -------------------------------------------------------
    # 3️⃣ Correlation Spike Simulation
    # -------------------------------------------------------
    def apply_correlation_spike(
        self,
        spike_duration: int = 10
    ) -> pd.DataFrame:

        stressed_returns = self.original_returns.copy()

        # Force assets to move together
        common_shock = stressed_returns.iloc[:spike_duration].mean(axis=1)

        for col in stressed_returns.columns:
            stressed_returns.loc[
                stressed_returns.index[:spike_duration], col
            ] = common_shock.values

        return stressed_returns
