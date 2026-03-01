from foundation import RunManager
from market_signal.engine import run
from market_signal.features import engineer_features

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt


# =========================================================
# 1. FEATURE ENGINEERING TEST
# =========================================================

def test_feature_engineering():

    print("\n==============================")
    print("FEATURE ENGINEERING TEST")
    print("==============================")

    df = pd.DataFrame({
        "open": np.random.rand(100),
        "high": np.random.rand(100),
        "low": np.random.rand(100),
        "close": np.random.rand(100),
        "volume": np.random.randint(1000, 5000, 100),
    })

    df.index = pd.date_range("2020-01-01", periods=100)

    result = engineer_features(df)

    print("\nFeature dataframe preview:")
    print(result.head())


# =========================================================
# 2. SIGNAL ENGINE RUN
# =========================================================

def test_signal_run():

    print("\n==============================")
    print("SIGNAL ENGINE RUN")
    print("==============================")

    run_id = RunManager.new_run()

    events = run(
        symbol="RELIANCE.NS",
        start="2019-01-01",
        end="2021-01-01",
        run_id=run_id
    )

    print("\nDetected Events:")
    for e in events:
        print(e)

    return run_id, events


# =========================================================
# 3. COVID VALIDATION
# =========================================================

def test_known_event(events):

    print("\n==============================")
    print("KNOWN EVENT VALIDATION")
    print("==============================")

    detected_dates = [e.event_timestamp.strftime("%Y-%m") for e in events]

    print("\nDetected months:")
    print(detected_dates)

    if any("2020-03" in d for d in detected_dates):
        print("\n✅ DETECTED COVID CRASH!")
    else:
        print("\n❌ COVID CRASH NOT DETECTED")


# =========================================================
# 4. LOAD JSONL EXPORT
# =========================================================

def load_jsonl(run_id):

    print("\n==============================")
    print("JSONL EXPORT CHECK")
    print("==============================")

    path = Path("data") / run_id / "signal" / "anomalies.jsonl"

    if not path.exists():
        print("JSONL not found:", path)
        return None

    df = pd.read_json(path, lines=True)

    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
    df = df.sort_values("event_timestamp")

    print("\nJSONL Preview:")
    print(df.head())

    return df


# =========================================================
# 5. PLOT SIGNAL STRENGTH
# =========================================================

def plot_full_signal_context(run_id, symbol="RELIANCE.NS"):

    print("\n==============================")
    print("FULL SIGNAL CONTEXT PLOT")
    print("==============================")

    # -----------------------------
    # Load anomaly JSONL
    # -----------------------------
    events_path = Path("data") / run_id / "signal" / "anomalies.jsonl"

    if not events_path.exists():
        print("No anomaly JSONL found")
        return

    events = pd.read_json(events_path, lines=True)
    events["event_timestamp"] = pd.to_datetime(events["event_timestamp"])
    events = events.sort_values("event_timestamp")

    # -----------------------------
    # Load raw price data again
    # (same range as events)
    # -----------------------------
    import yfinance as yf

    start = events["event_timestamp"].min() - pd.Timedelta(days=60)
    end = events["event_timestamp"].max() + pd.Timedelta(days=60)

    price = yf.download(symbol, start=start, end=end, progress=False)
    price.index = pd.to_datetime(price.index)

    # -----------------------------
    # PLOT
    # -----------------------------
    fig, ax_price = plt.subplots(figsize=(12, 6))

    # PRICE LINE
    ax_price.plot(price.index, price["Close"], label="Price")
    ax_price.set_ylabel("Price")
    ax_price.set_title(f"{symbol} — Price + Anomaly Signals")

    # -----------------------------
    # ANOMALY MARKERS
    # -----------------------------
    anomaly_prices = price.loc[events["event_timestamp"], "Close"]

    ax_price.scatter(
        events["event_timestamp"],
        anomaly_prices,
        s=120,
        marker="o",
        label="Anomaly Event"
    )

    # -----------------------------
    # SIGNAL STRENGTH (SECOND AXIS)
    # -----------------------------
    ax_signal = ax_price.twinx()

    ax_signal.plot(
        events["event_timestamp"],
        events["signal_strength"],
        linestyle="--",
        label="Signal Strength"
    )

    ax_signal.set_ylabel("Signal Strength (0–1)")

    # -----------------------------
    # LEGEND MERGE
    # -----------------------------
    lines1, labels1 = ax_price.get_legend_handles_labels()
    lines2, labels2 = ax_signal.get_legend_handles_labels()

    ax_price.legend(lines1 + lines2, labels1 + labels2)

    plt.grid(True)
    plt.tight_layout()
    plt.show()


# =========================================================
# MAIN RUNNER
# =========================================================

if __name__ == "__main__":

    print("\n\nPHASE-1 FULL SYSTEM TEST\n")

    test_feature_engineering()

    run_id, events = test_signal_run()

    test_known_event(events)

    df = load_jsonl(run_id)

    plot_full_signal_context(run_id)

    print("\n\nPHASE-1 INSPECTION COMPLETE\n")