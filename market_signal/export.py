import json
from pathlib import Path
from typing import List
from foundation import AnomalyEvent


def export_events_jsonl(
    events: List[AnomalyEvent],
    run_id: str,
    filename: str = "anomalies.jsonl"
):
    """
    Export anomaly events as newline-delimited JSON.

    Designed for plotting, analytics, notebooks.
    """

    if not events:
        return None

    out_dir = Path("data") / run_id / "signal"
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / filename

    with open(path, "w") as f:
        for e in events:
            record = {
                "run_id": e.run_id,
                "symbol": e.symbol,
                "event_timestamp": str(e.event_timestamp),
                "price_change_pct": e.price_change_pct,
                "signal_strength": e.anomaly_score,
                "model": e.model_name,
                "feature_window": e.feature_window,
                "data_hash": e.data_hash
            }
            f.write(json.dumps(record) + "\n")

    return path


def export_signal_timeline(df, run_id, filename="signal_timeline.jsonl"):

    out_dir = Path("data") / run_id / "signal"
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / filename

    with open(path, "w") as f:
        for idx, row in df.iterrows():

            record = {
                "run_id": run_id,
                "date": str(idx),
                "close": float(row.get("close", 0)),
                "log_return": float(row.get("log_return", 0)),
                "z_score": float(row.get("z_score", 0)),
                "volume_z": float(row.get("volume_z", 0)),
                "confidence": float(row.get("confidence", 0)),
                "anomaly_score": float(row.get("anomaly_score", 0)),
                "dtw_similarity": (
                    float(row["dtw_similarity"])
                    if "dtw_similarity" in row and not str(row["dtw_similarity"]) == "nan"
                    else None
                ),
                "is_anomaly": bool(row.get("is_anomaly", False)),
            }

            f.write(json.dumps(record) + "\n")

    return path