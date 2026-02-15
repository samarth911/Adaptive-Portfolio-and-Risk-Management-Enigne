# risk/volatility_targeting.py

def scale_by_volatility(current_vol, target_vol, weights):

    if current_vol == 0:
        return weights

    scale = target_vol / current_vol
    return {k: v * scale for k, v in weights.items()}
