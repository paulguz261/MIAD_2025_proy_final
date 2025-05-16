import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


class IsolationForestWithSeverity(BaseEstimator):
    """
        Esta clase permite entrenar un isolation forest y calcular un nivel de anomalia
        que depende de los quantiles del score resultado del entrenamiento en los datos 
        de entrenamiento
    """
    def __init__(self, n_estimators=100, contamination='auto', random_state=42):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.pipeline = None
        self.q01 = None
        self.q05 = None

    def fit(self, X, y=None):
        self.pipeline = make_pipeline(
            StandardScaler(),
            IsolationForest(
                n_estimators=self.n_estimators,
                contamination=self.contamination,
                random_state=self.random_state
            )
        )
        self.pipeline.fit(X)
        scores = self.pipeline.named_steps['isolationforest'].decision_function(
            self.pipeline.named_steps['standardscaler'].transform(X)
        )
        self.q01 = np.quantile(scores, 0.01)
        self.q05 = np.quantile(scores, 0.05)
        return self

    def predict(self, X):
        return self.pipeline.predict(X)

    def decision_function(self, X):
        return self.pipeline.decision_function(X)
    
    def predict_label(self, X):
        raw_preds = self.predict(X)
        return np.where(raw_preds == 1, 'normal', 'anomalía')

    def predict_severity(self, X):
        scores = self.decision_function(X)
        labels = self.predict(X)
        result = pd.DataFrame({
            'anomaly_score': scores,
            'anomaly_label': np.where(labels == 1, 'normal', 'anomalía')
        })
        result['nivel_anomalia_iforest'] = 'normal'
        mask_anomaly = result['anomaly_label'] == 'anomalía'
        result.loc[mask_anomaly, 'nivel_anomalia_iforest'] = result.loc[mask_anomaly, 'anomaly_score'].apply(
            lambda s: 'alta' if s <= self.q01 else ('media' if s <= self.q05 else 'leve')
        )
        return result["nivel_anomalia_iforest"]