# regime/ml_regime.py

from sklearn.cluster import KMeans

class MLRegimeDetector:

    def __init__(self, n_clusters=3):
        self.model = KMeans(n_clusters=n_clusters)

    def fit(self, feature_matrix):
        self.model.fit(feature_matrix)

    def predict(self, feature_matrix):
        return self.model.predict(feature_matrix)

