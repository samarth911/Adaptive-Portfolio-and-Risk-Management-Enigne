# backtest/rolling_window.py

def walk_forward_split(data, train_window, test_window):

    splits = []
    start = 0

    while (start + train_window + test_window) <= len(data):
        train = data.iloc[start:start+train_window]
        test = data.iloc[start+train_window:start+train_window+test_window]
        splits.append((train, test))
        start += test_window

    return splits
