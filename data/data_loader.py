# data/data_loader.py

import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Tuple


class DataLoader:
    """
    Responsible for:
    - Fetching historical price data
    - Cleaning missing values
    - Computing returns
    - Providing rolling train/test splits
    """

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        train_window: int = 756,   # ~3 years
        test_window: int = 126     # ~6 months
    ):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.train_window = train_window
        self.test_window = test_window

        self.price_data = None
        self.returns = None

    # -------------------------------------------------------
    # 1️⃣ Download Data
    # -------------------------------------------------------
    def download_data(self) -> pd.DataFrame:
        """
        Downloads close prices for given tickers.
        Handles:
        - Single ticker
        - Multiple tickers (MultiIndex columns)
        - Missing 'Adj Close'
        """

        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False,
            auto_adjust=False  # keep raw structure consistent
        )

        if data.empty:
            raise ValueError("No data downloaded. Check tickers or date range.")

        # ------------------------------
        # Handle MultiIndex (multiple tickers)
        # ------------------------------
        if isinstance(data.columns, pd.MultiIndex):

            # If Adjusted Close exists
            if "Adj Close" in data.columns.levels[0]:
                prices = data["Adj Close"]

            # Otherwise fallback to Close
            elif "Close" in data.columns.levels[0]:
                prices = data["Close"]

            else:
                raise ValueError("Neither 'Adj Close' nor 'Close' found in data.")

        # ------------------------------
        # Single ticker case
        # ------------------------------
        else:
            if "Adj Close" in data.columns:
                prices = data["Adj Close"]
            elif "Close" in data.columns:
                prices = data["Close"]
            else:
                raise ValueError("Neither 'Adj Close' nor 'Close' found in data.")

        # Clean data
        prices = prices.dropna(how="all")
        prices = prices.ffill().dropna()

        self.price_data = prices
        return self.price_data

    def compute_returns(self) -> pd.DataFrame:
        """
        Computes daily log returns.
        """
        if self.price_data is None:
            raise ValueError("Price data not loaded. Call download_data() first.")

        returns = np.log(self.price_data / self.price_data.shift(1))
        returns = returns.dropna()

        self.returns = returns
        return self.returns

    # -------------------------------------------------------
    # 3️⃣ Rolling Train/Test Split
    # -------------------------------------------------------
    def rolling_windows(self) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Generates rolling train/test splits.
        Prevents data leakage by ensuring future data is never included in training.
        """
        if self.returns is None:
            raise ValueError("Returns not computed. Call compute_returns() first.")

        splits = []
        total_length = len(self.returns)

        start = 0
        while (start + self.train_window + self.test_window) <= total_length:

            train = self.returns.iloc[start : start + self.train_window]
            test = self.returns.iloc[
                start + self.train_window :
                start + self.train_window + self.test_window
            ]

            splits.append((train, test))
            start += self.test_window  # walk forward

        return splits

    # -------------------------------------------------------
    # 4️⃣ Utility: Get Full Dataset
    # -------------------------------------------------------
    def get_full_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Returns price and returns.
        """
        if self.price_data is None:
            self.download_data()

        if self.returns is None:
            self.compute_returns()

        return self.price_data, self.returns
