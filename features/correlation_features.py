# features/correlation_features.py

import pandas as pd

def average_correlation(returns: pd.DataFrame, window: int = 63):
    rolling_corr = returns.rolling(window).corr()
    avg_corr = rolling_corr.groupby(level=0).mean()
    return avg_corr
