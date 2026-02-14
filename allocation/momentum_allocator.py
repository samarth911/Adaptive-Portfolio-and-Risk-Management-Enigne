# allocation/momentum_allocator.py

def momentum_weights(momentum_scores):

    positive = momentum_scores.clip(lower=0)
    weights = positive / positive.sum()

    return weights
