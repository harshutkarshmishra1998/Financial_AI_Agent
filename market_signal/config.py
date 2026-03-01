# signal/config.py

ISOLATION_FOREST_PARAMS = {
    "n_estimators": 200,
    "contamination": 0.03,
    "random_state": 42,
}

FEATURE_WINDOW = 30
CLUSTER_GAP_DAYS = 3
MIN_PRICE_MOVE_PCT = 2.0
DTW_WINDOW = 20