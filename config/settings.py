# config/settings.py

class Settings:

    # Risk Settings
    VOL_TARGET = 0.15
    MAX_DRAWDOWN_LIMIT = -0.20
    EXPOSURE_FLOOR = 0.2

    # Backtest Settings
    INITIAL_CAPITAL = 1_000_000
    REBALANCE_FREQUENCY = 21
    TRANSACTION_COST = 0.0005

    # Regime Thresholds
    VOL_THRESHOLD = 0.25
    DRAWDOWN_THRESHOLD = -0.15

    # Rolling Windows
    TRAIN_WINDOW = 756
    TEST_WINDOW = 126
