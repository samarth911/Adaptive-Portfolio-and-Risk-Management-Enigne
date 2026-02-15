# risk/drawdown_control.py

def apply_drawdown_cut(current_dd, limit, weights, floor):

    if current_dd < limit:
        return {k: v * floor for k, v in weights.items()}

    return weights
