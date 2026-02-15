# regime/rule_based_regime.py

def detect_regime(vol, drawdown, trend, vol_th, dd_th):

    if drawdown < dd_th:
        return "CRISIS"

    if vol > vol_th:
        return "HIGH_VOL"

    if trend > 0.5:
        return "BULL"

    return "BEAR"
