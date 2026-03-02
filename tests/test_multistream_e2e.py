import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import networkx as nx
import pandas as pd
# import pytest

from multistream_researcher.controller import Phase3Researcher
from multistream_researcher.storage import MultiStreamArtifactBuilder


def _find_latest_run_dir(data_root: Path = Path("data")) -> Path | None:
    run_dirs = sorted([p for p in data_root.glob("run_*") if p.is_dir()], key=lambda p: p.stat().st_mtime)
    return run_dirs[-1] if run_dirs else None


def _load_anomaly_nodes_edges(run_dir: Path) -> tuple[dict, list[str], list[tuple[str, str]]]:
    anomalies_path = run_dir / "signal" / "anomalies.jsonl"
    graphml_path = run_dir / "ecosystem_graph.graphml"

    if not anomalies_path.exists():
        raise FileNotFoundError(f"Missing anomalies file: {anomalies_path}")
    if not graphml_path.exists():
        raise FileNotFoundError(f"Missing graph structure file: {graphml_path}")

    df = pd.read_json(anomalies_path, lines=True)
    if df.empty:
        raise ValueError(f"No anomaly records found in: {anomalies_path}")

    last = df.iloc[-1]
    anomaly = {
        "timestamp": str(last["event_timestamp"]),
        "symbol": str(last["symbol"]),
    }

    graph = nx.read_graphml(graphml_path)
    graph_nodes = [str(n) for n in graph.nodes()]
    if not graph_nodes:
        raise ValueError(f"No graph nodes found in: {graphml_path}")

    graph_edges = [(str(u), str(v)) for u, v in graph.edges()]

    return anomaly, graph_nodes, graph_edges


def run_multistream_from_run_dir(run_dir: Path) -> dict:
    anomaly, graph_nodes, graph_edges = _load_anomaly_nodes_edges(run_dir)

    out_dir = run_dir / "multistream"
    builder = MultiStreamArtifactBuilder(data_dir=out_dir)
    manifest = builder.build(anomaly, graph_nodes)

    researcher = Phase3Researcher()
    researcher.ingest(anomaly, graph_nodes)
    results = researcher.retrieve(f"drivers behind move in {anomaly['symbol']}")

    if not results:
        raise AssertionError("No retrieval results produced by Phase3Researcher")

    return {
        "run_dir": str(run_dir),
        "manifest": manifest,
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges),
        "result_count": len(results),
    }


def test_multistream_pipeline_from_signal_graph_outputs():
    """
    End-to-end bridge test:
    - consumes run artifacts from tests/test_signal_graph.py output layout
    - builds multi-stream parquet/faiss artifacts
    - runs ingestion + retrieval via Phase3Researcher
    """
    run_id = os.getenv("RUN_ID")
    run_dir = Path("data") / run_id if run_id else _find_latest_run_dir(Path("data"))

    if run_dir is None or not run_dir.exists():
        raise AssertionError("No data/run_* found. Run tests/test_signal_graph.py first or set RUN_ID.")

    outcome = run_multistream_from_run_dir(run_dir)

    manifest_path = Path(outcome["manifest"].get("news_parquet", "")).parent / "manifest.json"
    assert manifest_path.exists(), "manifest.json should be generated in run_dir/multistream"
    assert outcome["result_count"] > 0


if __name__ == "__main__":
    run_id = os.getenv("RUN_ID")
    run_dir = Path("data") / run_id if run_id else _find_latest_run_dir(Path("data"))
    if run_dir is None:
        raise SystemExit("No data/run_* found. Run tests/test_signal_graph.py first or set RUN_ID.")

    out = run_multistream_from_run_dir(run_dir)
    print(json.dumps(out, indent=2))
