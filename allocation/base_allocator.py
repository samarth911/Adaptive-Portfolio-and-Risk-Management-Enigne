# allocation/base_allocator.py

import numpy as np
import pandas as pd
from typing import Dict


class BaseAllocator:
    """
    Allocates capital based on detected market regime.

    Regimes:
    - BULL
    - BEAR
    - HIGH_VOL
    - CRISIS
    """

    def __init__(self, tickers: list):
        self.tickers = tickers

    # -------------------------------------------------------
    # 1️⃣ Regime-Based Allocation Logic
    # -------------------------------------------------------
    def get_weights(self, regime: str) -> Dict[str, float]:

        n = len(self.tickers)

        # Default equal weight
        weights = {ticker: 1 / n for ticker in self.tickers}

        if regime == "BULL":
            # Heavy equity bias (assume first ticker is equity)
            weights = self._bull_allocation()

        elif regime == "BEAR":
            weights = self._bear_allocation()

        elif regime == "HIGH_VOL":
            weights = self._high_vol_allocation()

        elif regime == "CRISIS":
            weights = self._crisis_allocation()

        return weights

    # -------------------------------------------------------
    # Allocation Templates
    # -------------------------------------------------------

    def _bull_allocation(self):
        weights = {}
        for i, ticker in enumerate(self.tickers):
            if i == 0:  # assume first ticker = equity
                weights[ticker] = 0.7
            else:
                weights[ticker] = 0.3 / (len(self.tickers) - 1)
        return weights

    def _bear_allocation(self):
        weights = {}
        for i, ticker in enumerate(self.tickers):
            if i == 1:  # assume second ticker = bonds
                weights[ticker] = 0.6
            else:
                weights[ticker] = 0.4 / (len(self.tickers) - 1)
        return weights

    def _high_vol_allocation(self):
        # Balanced defensive positioning
        return {ticker: 1 / len(self.tickers) for ticker in self.tickers}

    def _crisis_allocation(self):
        weights = {}
        for i, ticker in enumerate(self.tickers):
            if i == 1: 
                weights[ticker] = 0.8
            else:
                weights[ticker] = 0.2 / (len(self.tickers) - 1)
        return weights
