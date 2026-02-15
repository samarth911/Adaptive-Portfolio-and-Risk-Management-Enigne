# stress_test/correlation_spike.py

import pandas as pd

def force_high_correlation(returns, duration=10):

    stressed = returns.copy()
    shock = stressed.iloc[:duration].mean(axis=1)

    for col in stressed.columns:
        stressed.loc[stressed.index[:duration], col] = shock.values

    return stressed
