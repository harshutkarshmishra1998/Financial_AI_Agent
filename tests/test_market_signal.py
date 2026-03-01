import argparse
from pathlib import Path

import pandas as pd

from foundation import RunManager
from market_signal.engine import run as run_signal
from market_signal.advanced_plots import (
    anomaly_heatmap,
    plot_full_signal_context,
    regime_visualizer,
    signal_vs_volatility,
)
from ecosystem_graph.runner import run as run_ecosystem
from ecosystem_graph.serializer import save_graph
from tests.test_foundation import clear_directory


def run_signal_engine(symbol: str, start: str, end: str):
    print("\n==============================")
    print("SIGNAL ENGINE RUN")
    print("==============================")

    run_id = RunManager.new_run()
    events = run_signal(symbol=symbol, start=start, end=end, run_id=run_id)

    print("\nDetected Events:")
    for event in events:
        print(event)

    return run_id, events


def run_ecosystem_engine(symbol: str, start: str, end: str, run_id: str):
    print("\n==============================")
    print("ECOSYSTEM GRAPH RUN")
    print("==============================")

    nodes, edges = run_ecosystem(symbol=symbol, start=start, end=end)

    graph_dir = Path("data") / run_id / "ecosystem"
    graph_dir.mkdir(parents=True, exist_ok=True)
    save_graph(nodes, edges, path=str(graph_dir) + "/")

    print(f"Graph saved: nodes={len(nodes)}, edges={len(edges)} @ {graph_dir}")
    return nodes, edges


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


def run_visual_analytics(run_id: str, symbol: str):
    print("\n==============================")
    print("ADVANCED VISUAL ANALYTICS")
    print("==============================")

    plot_full_signal_context(run_id, symbol)
    anomaly_heatmap(run_id)
    regime_visualizer(run_id)
    signal_vs_volatility(run_id)


def parse_args():
    parser = argparse.ArgumentParser(description="Run market signal + ecosystem graph pipeline")
    parser.add_argument("--symbol", type=str, required=True, help="Ticker symbol (e.g. TCS.NS)")
    parser.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip plot generation (useful in headless environments)",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Do not clear existing data/ before running",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("\n\nPHASE-1+2 FULL SYSTEM INSPECTION\n")

    if not args.keep_data:
        clear_directory("data")

    run_id, events = run_signal_engine(args.symbol, args.start, args.end)
    verify_json_export(run_id)
    run_ecosystem_engine(args.symbol, args.start, args.end, run_id)

    if not args.skip_plots:
        run_visual_analytics(run_id, args.symbol)

    print("\n\nPIPELINE INSPECTION COMPLETE\n")
