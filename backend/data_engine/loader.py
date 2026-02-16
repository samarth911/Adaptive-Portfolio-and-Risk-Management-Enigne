"""
Data Ingestion Engine: historical prices, rolling returns/vol/MA/correlations.
No look-ahead: all computations use only past data at each timestamp.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional

try:
    import yfinance as yf
except ImportError:
    yf = None


class DataEngine:
    """
    Single source of market data and derived series.
    - Pull historical prices
    - Compute: rolling returns, rolling vol, moving averages, rolling correlations
    - No data leakage (rolling windows only use past data).
    """

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        vol_window: int = 21,
        momentum_window: int = 63,
        trend_short: int = 50,
        trend_long: int = 200,
        corr_window: int = 63,
    ):
        self.tickers = tickers if isinstance(tickers, list) else [tickers]
        self.start_date = start_date
        self.end_date = end_date
        self.vol_window = vol_window
        self.momentum_window = momentum_window
        self.trend_short = trend_short
        self.trend_long = trend_long
        self.corr_window = corr_window

        self._prices: Optional[pd.DataFrame] = None
        self._returns: Optional[pd.DataFrame] = None
        self._features: Optional[dict] = None

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Download prices and compute log returns. Returns (prices, returns)."""
        if yf is None:
            raise ImportError("yfinance is required. pip install yfinance")
        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False,
            auto_adjust=False,
        )
        if data.empty:
            raise ValueError("No data downloaded. Check tickers or date range.")
        if isinstance(data.columns, pd.MultiIndex):
            if "Adj Close" in data.columns.levels[0]:
                prices = data["Adj Close"].copy()
            else:
                prices = data["Close"].copy()
        else:
            if "Adj Close" in data.columns:
                prices = data[["Adj Close"]].copy()
            else:
                prices = data[["Close"]].copy()
            if len(self.tickers) == 1:
                prices.columns = [self.tickers[0]]
        prices = prices.dropna(how="all").ffill().dropna()
        returns = np.log(prices / prices.shift(1)).dropna()
        self._prices = prices
        self._returns = returns
        return prices, returns

    def get_prices(self) -> pd.DataFrame:
        if self._prices is None:
            self.load()
        return self._prices

    def get_returns(self) -> pd.DataFrame:
        if self._returns is None:
            self.load()
        return self._returns

    def rolling_volatility(self) -> pd.DataFrame:
        """Annualized rolling volatility (past data only)."""
        r = self.get_returns()
        return r.rolling(self.vol_window, min_periods=1).std() * np.sqrt(252)

    def rolling_momentum(self) -> pd.DataFrame:
        """Rolling mean return (momentum proxy)."""
        return self.get_returns().rolling(self.momentum_window, min_periods=1).mean()

    def moving_average_trend(self) -> pd.DataFrame:
        """Trend: short MA > long MA (1/0)."""
        p = self.get_prices()
        short = p.rolling(self.trend_short, min_periods=1).mean()
        long_ma = p.rolling(self.trend_long, min_periods=1).mean()
        return (short > long_ma).astype(int)

    def rolling_drawdown(self) -> pd.DataFrame:
        """Rolling drawdown from cumulative max (per-asset)."""
        p = self.get_prices()
        cummax = p.cummax()
        return (p - cummax) / cummax.replace(0, np.nan)

    def rolling_correlation(self) -> pd.DataFrame:
        """Rolling correlation (returns). For heatmap use last slice or average."""
        return self.get_returns().rolling(self.corr_window, min_periods=1).corr()

    def get_features(self) -> dict:
        """All features needed for regime and allocation. No leakage."""
        if self._features is not None:
            return self._features

        returns_df = self.get_returns()
        
        # Align all generated features to the returns index to ensure consistent length
        common_index = returns_df.index
        
        volatility = self.rolling_volatility().loc[common_index]
        momentum = self.rolling_momentum().loc[common_index]
        trend_signal = self.moving_average_trend().loc[common_index]
        drawdown = self.rolling_drawdown().loc[common_index]
        correlation = self.rolling_correlation() # rolling_correlation is complex, handle alignment carefully

        self._features = {
            "returns": returns_df,
            "volatility": volatility,
            "momentum": momentum,
            "trend_signal": trend_signal,
            "drawdown": drawdown,
            "correlation": correlation,
        }
        return self._features

    def rolling_windows(
        self, train_window: int = 756, test_window: int = 126
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
        """Walk-forward splits: (train_returns, test_returns, train_prices, test_prices)."""
        returns = self.get_returns()
        prices = self.get_prices()
        total = len(returns)
        splits = []
        start = 0
        while start + train_window + test_window <= total:
            train_ret = returns.iloc[start : start + train_window]
            test_ret = returns.iloc[start + train_window : start + train_window + test_window]
            train_pr = prices.iloc[start : start + train_window]
            test_pr = prices.iloc[start + train_window : start + train_window + test_window]
            splits.append((train_ret, test_ret, train_pr, test_pr))
            start += test_window
        return splits
