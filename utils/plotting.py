# utils/plotting.py

import matplotlib.pyplot as plt

def plot_equity_curve(equity_curve):
    equity_curve.plot()
    plt.title("Portfolio Equity Curve")
    plt.show()
