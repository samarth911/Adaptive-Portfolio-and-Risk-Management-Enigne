import yfinance as yf
import pandas as pd

def download_stock_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date)
        data[ticker] = df
    return data