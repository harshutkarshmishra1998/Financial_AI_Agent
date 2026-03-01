from foundation import RunManager
from market_signal.engine import run
from market_signal.features import engineer_features

from market_signal.advanced_plots import (
    plot_full_signal_context,
    anomaly_heatmap,
    regime_visualizer,
    signal_vs_volatility,
    multi_symbol_overlay
)

import pandas as pd
import numpy as np
from pathlib import Path

from tests.test_foundation import clear_directory


# =========================================================
# 1️⃣ FEATURE ENGINEERING TEST
# =========================================================

# def feature_engineering_test():

#     print("\n==============================")
#     print("FEATURE ENGINEERING TEST")
#     print("==============================")

#     df = pd.DataFrame({
#         "open": np.random.rand(100),
#         "high": np.random.rand(100),
#         "low": np.random.rand(100),
#         "close": np.random.rand(100),
#         "volume": np.random.randint(1000, 5000, 100),
#     })

#     df.index = pd.date_range("2020-01-01", periods=100)

#     result = engineer_features(df)

#     print("\nFeature dataframe preview:")
#     print(result.head())


# =========================================================
# 2️⃣ SIGNAL ENGINE RUN
# =========================================================

ticker = "TCS.NS"

def run_signal_engine():

    print("\n==============================")
    print("SIGNAL ENGINE RUN")
    print("==============================")

    run_id = RunManager.new_run()

    events = run(
        # symbol="RELIANCE.NS",
        symbol=ticker,
        start="2019-01-01",
        end="2021-01-01",
        run_id=run_id
    )

    print("\nDetected Events:")
    for e in events:
        print(e)

    return run_id, events


# =========================================================
# 3️⃣ KNOWN EVENT VALIDATION
# =========================================================

def validate_known_event(events):

    print("\n==============================")
    print("KNOWN EVENT VALIDATION")
    print("==============================")

    detected_months = [
        e.event_timestamp.strftime("%Y-%m")
        for e in events
    ]

    print("\nDetected months:")
    print(detected_months)

    if any("2020-03" in m for m in detected_months):
        print("\n✅ DETECTED COVID CRASH!")
    else:
        print("\n❌ COVID CRASH NOT DETECTED")


# =========================================================
# 4️⃣ JSONL CHECK
# =========================================================

def verify_json_export(run_id):

    print("\n==============================")
    print("JSON EXPORT CHECK")
    print("==============================")

    path = Path("data") / run_id / "signal" / "anomalies.jsonl"

    if not path.exists():
        print("❌ anomalies.jsonl not found")
        return None

    df = pd.read_json(path, lines=True)
    print("\nJSONL Preview:")
    print(df.head())

    return df


# =========================================================
# 5️⃣ VISUAL ANALYTICS
# =========================================================

def run_visual_analytics(run_id):

    print("\n==============================")
    print("ADVANCED VISUAL ANALYTICS")
    print("==============================")

    # full market context (offline)
    plot_full_signal_context(run_id, ticker)

    # heatmap
    anomaly_heatmap(run_id)

    # regime segmentation
    regime_visualizer(run_id)

    # phase diagram
    signal_vs_volatility(run_id)

    # overlay (single run example)
    # multi_symbol_overlay([run_id])


# =========================================================
# MAIN RUNNER
# =========================================================

if __name__ == "__main__":

    print("\n\nPHASE-1 FULL SYSTEM INSPECTION\n")

    clear_directory("data")

    # feature_engineering_test()

    run_id, events = run_signal_engine()

    validate_known_event(events)

    verify_json_export(run_id)

    run_visual_analytics(run_id)

    print("\n\nPHASE-1 INSPECTION COMPLETE\n")