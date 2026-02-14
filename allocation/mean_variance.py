# allocation/mean_variance.py

import numpy as np

def mean_variance_weights(expected_returns, cov_matrix, risk_aversion=1):

    inv_cov = np.linalg.inv(cov_matrix)
    weights = inv_cov @ expected_returns
    weights /= weights.sum()

    return weights
