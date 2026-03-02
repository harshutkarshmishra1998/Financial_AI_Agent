import shutil

import matplotlib
matplotlib.use("Agg")  # disable GUI completely

import concurrent.futures
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

from foundation import RunManager
from market_signal.engine import run as run_signal_engine
from market_signal.advanced_plots import (
    plot_full_signal_context,
    anomaly_heatmap,
    regime_visualizer,
    signal_vs_volatility,
)

from ecosystem_graph.pipeline import EcosystemPipeline
from ecosystem_graph.visualize_graph import draw_ecosystem_graph


def clear_directory(folder_path: str | Path):
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Directory not found → {folder}")
        return

    for item in folder.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print(f"Cleared everything inside → {folder}")


TICKER = "RELIANCE.NS"
START_DATE = "2019-01-01"
END_DATE = "2024-01-01"
UNIVERSE_PATH = "universe/market_universe.parquet"
DATA_ROOT = Path("data")

import matplotlib.pyplot as plt
from pathlib import Path

PLOT_COUNTER = 0

def run_full_system():

    clear_directory("data")

    DATA_ROOT.mkdir(exist_ok=True)

    run_id = RunManager.new_run()
    run_dir = DATA_ROOT / run_id  # FIXED
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run ID → {run_id}")

    # -------------------------
    # 1️⃣ Run heavy computation in parallel
    # -------------------------
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        f_signal = executor.submit(
            run_signal_engine,
            symbol=TICKER,
            start=START_DATE,
            end=END_DATE,
            run_id=run_id
        )

        f_graph = executor.submit(
            lambda: EcosystemPipeline(UNIVERSE_PATH).run(TICKER)
        )

        events = f_signal.result()
        nodes, edges = f_graph.result()

    # -------------------------
    # 2️⃣ Generate ecosystem graph
    # -------------------------
    draw_ecosystem_graph(
        nodes,
        edges,
        output_file=str(run_dir / "ecosystem_graph.html")
    )

    # -------------------------
    # 3️⃣ Plot sequentially (main thread only)
    # -------------------------
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    plot_full_signal_context(run_id, TICKER)
    plt.savefig(plots_dir / "full_context.png")
    plt.close()

    anomaly_heatmap(run_id)
    plt.savefig(plots_dir / "heatmap.png")
    plt.close()

    regime_visualizer(run_id)
    plt.savefig(plots_dir / "regime.png")
    plt.close()

    signal_vs_volatility(run_id)
    plt.savefig(plots_dir / "phase.png")
    plt.close()

    print(f"All outputs saved → {run_dir}")


if __name__ == "__main__":
    run_full_system()