from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# =========================================================
# INTERNAL LOADER
# =========================================================

def _load_timeline(run_id):
    path = Path("data") / run_id / "signal" / "signal_timeline.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Missing timeline for run {run_id}")

    df = pd.read_json(path, lines=True)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


# =========================================================
# 3️⃣ MULTI SYMBOL OVERLAY
# =========================================================

def multi_symbol_overlay(run_ids):

    plt.figure(figsize=(12,5))

    for run_id in run_ids:
        path = Path("data") / run_id / "signal" / "anomalies.jsonl"
        df = pd.read_json(path, lines=True)
        df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])

        plt.scatter(
            df["event_timestamp"],
            df["signal_strength"],
            label=run_id,
            s=80
        )

    plt.title("Multi-Symbol Anomaly Overlay")
    plt.xlabel("Date")
    plt.ylabel("Signal Strength")
    plt.legend()
    plt.grid(True)
    # plt.show()


# =========================================================
# 4️⃣ ANOMALY HEATMAP TIMELINE
# =========================================================

def anomaly_heatmap(run_id):

    df = _load_timeline(run_id)

    df["month"] = df.index.to_period("M") #type: ignore
    monthly = df.groupby("month")["confidence"].mean()

    data = np.array(monthly).reshape(1, -1)

    plt.figure(figsize=(14,2))
    sns.heatmap(
        data,
        cmap="viridis",
        cbar=True
    )
    plt.title("Monthly Anomaly Intensity")
    plt.yticks([])
    plt.xticks(rotation=45)
    # plt.show()


# =========================================================
# 5️⃣ REGIME SEGMENTATION VISUALIZER
# =========================================================

def regime_visualizer(run_id, threshold=0.7):

    df = _load_timeline(run_id)

    df["regime"] = df["confidence"] > threshold

    plt.figure(figsize=(12,4))
    plt.plot(df.index, df["regime"].astype(int))
    plt.title("High-Volatility Regime Detection")
    plt.ylabel("Regime (1 = High)")
    plt.grid(True)
    # plt.show()


# =========================================================
# 6️⃣ SIGNAL vs VOLATILITY PHASE DIAGRAM
# =========================================================

def signal_vs_volatility(run_id):

    df = _load_timeline(run_id)

    plt.figure(figsize=(6,6))
    plt.scatter(
        df["z_score"],
        df["confidence"],
        alpha=0.6
    )

    plt.xlabel("Z-Score (Volatility)")
    plt.ylabel("Anomaly Confidence")
    plt.title("Signal vs Volatility Phase Space")
    plt.grid(True)
    # plt.show()

# =========================================================
# FULL SIGNAL CONTEXT PLOT (OFFLINE — NO API)
# =========================================================

def plot_full_signal_context(run_id, symbol=None):

    # print("\n==============================")
    # print("FULL SIGNAL CONTEXT PLOT")
    # print("==============================")

    # -----------------------------
    # load timeline (contains price + features)
    # -----------------------------
    df = _load_timeline(run_id)

    # -----------------------------
    # load anomaly events
    # -----------------------------
    events_path = Path("data") / run_id / "signal" / "anomalies.jsonl"

    if not events_path.exists():
        print("No anomaly JSONL found")
        return

    events = pd.read_json(events_path, lines=True)
    events["event_timestamp"] = pd.to_datetime(events["event_timestamp"])

    # align prices at anomaly timestamps
    anomaly_prices = df.loc[events["event_timestamp"], "close"]

    # -----------------------------
    # plot
    # -----------------------------
    fig, ax_price = plt.subplots(figsize=(12, 6))

    # price line
    ax_price.plot(df.index, df["close"], label="Price")

    # anomaly markers
    ax_price.scatter(
        events["event_timestamp"],
        anomaly_prices,
        s=120,
        label="Anomaly Event"
    )

    ax_price.set_ylabel("Price")

    if symbol:
        ax_price.set_title(f"{symbol} — Price + Anomaly Signals")
    else:
        ax_price.set_title("Price + Anomaly Signals")

    # -----------------------------
    # signal strength axis
    # -----------------------------
    ax_signal = ax_price.twinx()

    ax_signal.plot(
        events["event_timestamp"],
        events["signal_strength"],
        linestyle="--",
        label="Signal Strength"
    )

    ax_signal.set_ylabel("Signal Strength")

    # merge legends
    l1, lab1 = ax_price.get_legend_handles_labels()
    l2, lab2 = ax_signal.get_legend_handles_labels()

    ax_price.legend(l1 + l2, lab1 + lab2)

    plt.grid(True)
    plt.tight_layout()
    # plt.show()