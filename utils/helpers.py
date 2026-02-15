# utils/helpers.py

def normalize_weights(weights):
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}
