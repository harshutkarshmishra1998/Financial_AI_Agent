import numpy as np
from foundation import ArtifactStore, AnomalyEvent, data_hash, now

from .data import fetch_ohlcv
from .features import engineer_features
from .detector import detect_anomalies
from .cluster import cluster_events
from .dtw import rolling_dtw
from .config import MIN_PRICE_MOVE_PCT
from .export import export_events_jsonl
from .export import export_signal_timeline

# helper
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

# main engin
def run(symbol, start, end, run_id):

    # data ingestion
    raw = fetch_ohlcv(symbol, start, end)
    raw_hash = data_hash(raw)

    # feature pipeline
    df = engineer_features(raw)
    df = detect_anomalies(df)

    # DTW structural similarity
    try:
        dtw_series = rolling_dtw(raw)
        df["dtw_similarity"] = np.nan
        df.iloc[len(df) - len(dtw_series):, df.columns.get_loc("dtw_similarity")] = dtw_series
    except Exception:
        df["dtw_similarity"] = np.nan

    # clustering
    clusters = cluster_events(df)

    artifacts = []

    for cluster in clusters:

        event_date = _cluster_representative(df, cluster)
        row = df.loc[event_date]

        price_move = _safe_price_change(raw, event_date)

        # minimum economic significance
        if abs(price_move) < MIN_PRICE_MOVE_PCT: #type: ignore
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
                price_change_pct=float(price_move), #type: ignore
                data_hash=raw_hash,
                model_name="Isolation_Forest_v1",
                feature_window="30d",
            )
        )

    if artifacts:
        ArtifactStore.write(artifacts, "anomalies")
        export_events_jsonl(artifacts, run_id)
        export_signal_timeline(df, run_id)

    return artifacts