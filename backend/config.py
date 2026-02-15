"""Central configuration for the portfolio engine."""

# Risk
VOL_TARGET = 0.15
MAX_DRAWDOWN_LIMIT = -0.20
EXPOSURE_FLOOR = 0.2
VOL_THRESHOLD = 0.25
DRAWDOWN_THRESHOLD = -0.15

# Backtest
INITIAL_CAPITAL = 1_000_000
REBALANCE_FREQUENCY = 21
TRANSACTION_COST = 0.0005
TRAIN_WINDOW = 756
TEST_WINDOW = 126

# Suspicious metrics (flag if exceeded)
SHARPE_SUSPICIOUS = 3.0
CALMAR_SUSPICIOUS = 5.0

# Regime labels (unified)
REGIME_TRENDING_UP = "TRENDING_UP"
REGIME_TRENDING_DOWN = "TRENDING_DOWN"
REGIME_HIGH_VOL = "HIGH_VOL"
REGIME_CRASH = "CRASH"

# Risk levels (user-selectable)
RISK_LEVELS = {
    "LOW": {"vol_target": 0.10, "max_drawdown_limit": -0.12, "exposure_floor": 0.15},
    "MEDIUM": {"vol_target": 0.15, "max_drawdown_limit": -0.20, "exposure_floor": 0.20},
    "HIGH": {"vol_target": 0.22, "max_drawdown_limit": -0.28, "exposure_floor": 0.25},
}
