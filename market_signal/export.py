# signal/export.py

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