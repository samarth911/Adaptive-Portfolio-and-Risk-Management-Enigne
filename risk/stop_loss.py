# risk/stop_loss.py

def apply_stop_loss(asset_return, threshold, weight):

    if asset_return < threshold:
        return 0

    return weight
