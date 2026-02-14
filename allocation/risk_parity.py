# allocation/risk_parity.py

import numpy as np

def risk_parity_weights(cov_matrix):

    inv_vol = 1 / np.sqrt(np.diag(cov_matrix))
    weights = inv_vol / inv_vol.sum()

    return weights
