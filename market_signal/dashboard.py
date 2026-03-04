import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def four_panel_dashboard(run_id):

    path = Path("data") / run_id / "signal" / "signal_timeline.jsonl"
    df = pd.read_json(path, lines=True)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

    # PRICE + ANOMALY
    axes[0].plot(df.index, df["close"])
    axes[0].scatter(
        df[df["is_anomaly"]].index,
        df[df["is_anomaly"]]["close"],
        s=60
    )
    axes[0].set_title("Price + Anomaly Events")

    # SIGNAL STRENGTH
    axes[1].plot(df.index, df["confidence"])
    axes[1].set_title("Anomaly Confidence")

    # Z-SCORE
    axes[2].plot(df.index, df["z_score"])
    axes[2].set_title("Return Z-Score")

    # DTW + VOLATILITY
    axes[3].plot(df.index, df["dtw_similarity"])
    axes[3].set_title("DTW Similarity")

    plt.tight_layout()
    plt.show()