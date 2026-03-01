# signal/detector.py

# import numpy as np
# from sklearn.ensemble import IsolationForest
# from .config import ISOLATION_FOREST_PARAMS


# def detect_anomalies(df):

#     features = df[["log_return", "z_score", "volume_z"]].values

#     model = IsolationForest(**ISOLATION_FOREST_PARAMS)

#     model.fit(features)

#     scores = model.decision_function(features)
#     preds = model.predict(features)

#     df["anomaly_score"] = -scores
#     df["is_anomaly"] = preds == -1

#     return df

# signal/detector.py

import numpy as np
from sklearn.ensemble import IsolationForest
from .config import ISOLATION_FOREST_PARAMS


def _normalize_scores(scores: np.ndarray):
    """Convert raw anomaly scores to 0–1 confidence."""
    s_min = scores.min()
    s_max = scores.max()

    if s_max == s_min:
        return np.zeros_like(scores)

    return (scores - s_min) / (s_max - s_min)


def detect_anomalies(df):

    features = df[["log_return", "z_score", "volume_z"]].values

    model = IsolationForest(**ISOLATION_FOREST_PARAMS)
    model.fit(features)

    raw_scores = -model.decision_function(features)
    preds = model.predict(features)

    confidence = _normalize_scores(raw_scores)

    df["anomaly_score"] = raw_scores
    df["confidence"] = confidence
    df["is_anomaly"] = preds == -1

    return df