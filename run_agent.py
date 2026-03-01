from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

def run_full_pipeline(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    One-function entrypoint for end-to-end execution:
    1) Runs market signal phase.
    2) Builds ecosystem graph from the same symbol/timeframe.
    3) Persists graph artifacts under data/<run_id>/ecosystem.

    Returns run metadata with paths and counts.
    """

    from foundation import RunManager
    from market_signal.engine import run as run_market_signal
    from ecosystem_graph.runner import run as run_ecosystem_graph
    from ecosystem_graph.serializer import save_graph

    run_id = RunManager.new_run()

    anomalies = run_market_signal(
        symbol=symbol,
        start=start_date,
        end=end_date,
        run_id=run_id,
    )

    nodes, edges = run_ecosystem_graph(
        symbol=symbol,
        start=start_date,
        end=end_date,
    )

    graph_dir = Path("data") / run_id / "ecosystem"
    save_graph(nodes, edges, path=str(graph_dir) + "/")

    summary = {
        "run_id": run_id,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "anomaly_count": len(anomalies),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "graph_nodes_path": str(graph_dir / "nodes.parquet"),
        "graph_edges_path": str(graph_dir / "edges.parquet"),
    }

    summary_path = graph_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    summary["summary_path"] = str(summary_path)

    return summary


def _parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Run full Financial AI pipeline")
    parser.add_argument("--symbol", required=True, help="Ticker symbol, e.g. TCS.NS")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = run_full_pipeline(args.symbol, args.start, args.end)
    print(json.dumps(result, indent=2))
