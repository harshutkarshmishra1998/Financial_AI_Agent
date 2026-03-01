# # market_signal/engine.py

# from foundation import ArtifactStore, AnomalyEvent, data_hash
# from .data import fetch_ohlcv
# from .features import engineer_features
# from .detector import detect_anomalies
# from .cluster import cluster_events
# from .config import MIN_PRICE_MOVE_PCT


# def run(symbol: str, start: str, end: str, run_id: str):

#     # ---------------------------------------------------
#     # 1. Fetch Raw Data
#     # ---------------------------------------------------
#     raw = fetch_ohlcv(symbol, start, end)

#     if raw.empty:
#         return []

#     raw = raw.sort_index()
#     raw = raw[~raw.index.duplicated(keep="first")]

#     raw_hash = data_hash(raw)

#     # ---------------------------------------------------
#     # 2. Feature Engineering
#     # ---------------------------------------------------
#     df = engineer_features(raw)

#     if df.empty:
#         return []

#     df = df.sort_index()
#     df = df[~df.index.duplicated(keep="first")]

#     # Align strictly to raw index intersection
#     df = df.loc[df.index.intersection(raw.index)]

#     # ---------------------------------------------------
#     # 3. Anomaly Detection
#     # ---------------------------------------------------
#     df = detect_anomalies(df)

#     # ---------------------------------------------------
#     # 4. Cluster Anomalies
#     # ---------------------------------------------------
#     clusters = cluster_events(df)

#     artifacts = []

#     # ---------------------------------------------------
#     # 5. Build Events
#     # ---------------------------------------------------
#     for cluster in clusters:

#         event_date = cluster[0]

#         # ensure timestamp alignment
#         if event_date not in raw.index:
#             continue

#         # locate row position safely
#         idx = raw.index.get_indexer([event_date])[0]

#         if idx <= 0:
#             continue

#         prev_close = raw.iloc[idx - 1]["close"]
#         curr_close = raw.iloc[idx]["close"]

#         # enforce scalar extraction
#         prev_close = float(prev_close)
#         curr_close = float(curr_close)

#         if prev_close == 0:
#             continue

#         price_move = (curr_close - prev_close) / prev_close * 100.0

#         if abs(price_move) < float(MIN_PRICE_MOVE_PCT):
#             continue

#         # safe feature row extraction
#         if event_date not in df.index:
#             continue

#         row = df.loc[event_date]

#         # if somehow multiple rows, pick first
#         if hasattr(row, "ndim") and row.ndim > 1:
#             row = row.iloc[0]

#         anomaly_score = float(row["anomaly_score"])

#         artifacts.append(
#             AnomalyEvent(
#                 run_id=run_id,
#                 phase="signal",
#                 event_timestamp=event_date,
#                 symbol=symbol,
#                 anomaly_score=anomaly_score,
#                 price_change_pct=float(price_move),
#                 data_hash=raw_hash,
#                 model_name="IsolationForest_v1",
#                 feature_window="30d",
#             )
#         )

#     # ---------------------------------------------------
#     # 6. Persist
#     # ---------------------------------------------------
#     if artifacts:
#         ArtifactStore.write(artifacts, "anomalies")

#     return artifacts

# signal/engine.py

import numpy as np
from foundation import ArtifactStore, AnomalyEvent, data_hash, now

from .data import fetch_ohlcv
from .features import engineer_features
from .detector import detect_anomalies
from .cluster import cluster_events
from .dtw import rolling_dtw
from .config import MIN_PRICE_MOVE_PCT
from .export import export_events_jsonl


# ---------------------------------------------------
# helpers
# ---------------------------------------------------

def _safe_price_change(raw, event_date):
    """Robust previous-close lookup."""
    loc = raw.index.get_loc(event_date)

    if loc == 0:
        return 0.0

    prev_close = raw.iloc[loc - 1]["close"]
    curr_close = raw.iloc[loc]["close"]

    return ((curr_close - prev_close) / prev_close) * 100


def _cluster_representative(df, cluster):
    """
    Select strongest event in cluster.
    Uses weighted signal strength.
    """
    sub = df.loc[cluster]

    strength = (
        0.5 * sub["confidence"]
        + 0.3 * np.abs(sub["z_score"])
        + 0.2 * np.abs(sub["volume_z"])
    )

    return sub.iloc[strength.argmax()].name


# ---------------------------------------------------
# main engine
# ---------------------------------------------------

def run(symbol, start, end, run_id):

    # -------------------------
    # data ingestion
    # -------------------------
    raw = fetch_ohlcv(symbol, start, end)
    raw_hash = data_hash(raw)

    # -------------------------
    # feature pipeline
    # -------------------------
    df = engineer_features(raw)
    df = detect_anomalies(df)

    # -------------------------
    # DTW structural similarity
    # -------------------------
    try:
        dtw_series = rolling_dtw(raw)
        df["dtw_similarity"] = np.nan
        df.iloc[len(df) - len(dtw_series):, df.columns.get_loc("dtw_similarity")] = dtw_series
    except Exception:
        df["dtw_similarity"] = np.nan

    # -------------------------
    # clustering
    # -------------------------
    clusters = cluster_events(df)

    artifacts = []

    for cluster in clusters:

        event_date = _cluster_representative(df, cluster)
        row = df.loc[event_date]

        price_move = _safe_price_change(raw, event_date)

        # minimum economic significance
        if abs(price_move) < MIN_PRICE_MOVE_PCT:
            continue

        # composite signal strength
        signal_strength = (
            0.6 * row["confidence"]
            + 0.3 * abs(price_move) / 10
            + 0.1 * (row["dtw_similarity"] if not np.isnan(row["dtw_similarity"]) else 0)
        )

        artifacts.append(
            AnomalyEvent(
                run_id=run_id,
                phase="signal",
                event_timestamp=event_date,
                symbol=symbol,
                anomaly_score=float(signal_strength),
                price_change_pct=float(price_move),
                data_hash=raw_hash,
                model_name="IsolationForest_v2_hardened",
                feature_window="30d",
            )
        )

    if artifacts:
        ArtifactStore.write(artifacts, "anomalies")
        export_events_jsonl(artifacts, run_id)

    return artifacts