# signal/detector.py

import numpy as np
from sklearn.ensemble import IsolationForest
from .config import ISOLATION_FOREST_PARAMS


def detect_anomalies(df):

    features = df[["log_return", "z_score", "volume_z"]].values

    model = IsolationForest(**ISOLATION_FOREST_PARAMS)

    model.fit(features)

    scores = model.decision_function(features)
    preds = model.predict(features)

    df["anomaly_score"] = -scores
    df["is_anomaly"] = preds == -1

    return df