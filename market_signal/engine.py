# market_signal/engine.py

from foundation import ArtifactStore, AnomalyEvent, data_hash
from .data import fetch_ohlcv
from .features import engineer_features
from .detector import detect_anomalies
from .cluster import cluster_events
from .config import MIN_PRICE_MOVE_PCT


def run(symbol: str, start: str, end: str, run_id: str):

    # ---------------------------------------------------
    # 1. Fetch Raw Data
    # ---------------------------------------------------
    raw = fetch_ohlcv(symbol, start, end)

    if raw.empty:
        return []

    raw = raw.sort_index()
    raw = raw[~raw.index.duplicated(keep="first")]

    raw_hash = data_hash(raw)

    # ---------------------------------------------------
    # 2. Feature Engineering
    # ---------------------------------------------------
    df = engineer_features(raw)

    if df.empty:
        return []

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]

    # Align strictly to raw index intersection
    df = df.loc[df.index.intersection(raw.index)]

    # ---------------------------------------------------
    # 3. Anomaly Detection
    # ---------------------------------------------------
    df = detect_anomalies(df)

    # ---------------------------------------------------
    # 4. Cluster Anomalies
    # ---------------------------------------------------
    clusters = cluster_events(df)

    artifacts = []

    # ---------------------------------------------------
    # 5. Build Events
    # ---------------------------------------------------
    for cluster in clusters:

        event_date = cluster[0]

        # ensure timestamp alignment
        if event_date not in raw.index:
            continue

        # locate row position safely
        idx = raw.index.get_indexer([event_date])[0]

        if idx <= 0:
            continue

        prev_close = raw.iloc[idx - 1]["close"]
        curr_close = raw.iloc[idx]["close"]

        # enforce scalar extraction
        prev_close = float(prev_close)
        curr_close = float(curr_close)

        if prev_close == 0:
            continue

        price_move = (curr_close - prev_close) / prev_close * 100.0

        if abs(price_move) < float(MIN_PRICE_MOVE_PCT):
            continue

        # safe feature row extraction
        if event_date not in df.index:
            continue

        row = df.loc[event_date]

        # if somehow multiple rows, pick first
        if hasattr(row, "ndim") and row.ndim > 1:
            row = row.iloc[0]

        anomaly_score = float(row["anomaly_score"])

        artifacts.append(
            AnomalyEvent(
                run_id=run_id,
                phase="signal",
                event_timestamp=event_date,
                symbol=symbol,
                anomaly_score=anomaly_score,
                price_change_pct=float(price_move),
                data_hash=raw_hash,
                model_name="IsolationForest_v1",
                feature_window="30d",
            )
        )

    # ---------------------------------------------------
    # 6. Persist
    # ---------------------------------------------------
    if artifacts:
        ArtifactStore.write(artifacts, "anomalies")

    return artifacts