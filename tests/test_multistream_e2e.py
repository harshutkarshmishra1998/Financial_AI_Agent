import json
import os
import pickle
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import networkx as nx
import pandas as pd

from multistream_researcher.controller import Phase3Researcher
from multistream_researcher.llm_driver_ranker import LLMDriverRanker
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


def _save_filtered_graph_artifacts(
    run_dir: Path,
    selected_nodes: list[str],
    graph_edges: list[tuple[str, str]],
) -> tuple[Path, Path]:
    selected = set(selected_nodes)
    filtered_edges = [(u, v) for u, v in graph_edges if u in selected and v in selected]

    filtered_graph = nx.DiGraph()
    filtered_graph.add_nodes_from(selected_nodes)
    filtered_graph.add_edges_from(filtered_edges)

    graphml_path = run_dir / "ecosystem_graph_filtered_llm.graphml"
    pkl_path = run_dir / "ecosystem_graph_filtered_llm.pkl"

    nx.write_graphml(filtered_graph, graphml_path)
    with pkl_path.open("wb") as f:
        pickle.dump(filtered_graph, f)

    return graphml_path, pkl_path


def _timed_step(label: str, fn):
    start = time.perf_counter()
    print(f"\n[START] {label}")
    value = fn()
    elapsed = time.perf_counter() - start
    print(f"[DONE]  {label} ({elapsed:.2f}s)")
    return value, elapsed


def run_multistream_from_run_dir(run_dir: Path) -> dict:
    (anomaly, graph_nodes, graph_edges), load_sec = _timed_step(
        "Load anomaly + graph artifacts",
        lambda: _load_anomaly_nodes_edges(run_dir),
    )

    ranker = LLMDriverRanker()
    selected_nodes, rank_sec = _timed_step(
        "LLM node filtering",
        lambda: ranker.rank(anomaly, graph_nodes),
    )
    if not selected_nodes:
        selected_nodes = graph_nodes[:6]

    print(
        "[INFO] Node counts before multistream researcher → "
        f"original: {len(graph_nodes)}, after LLM filter: {len(selected_nodes)}"
    )
    print("[INFO] Original nodes:")
    print(graph_nodes)
    print("[INFO] LLM-filtered nodes:")
    print(selected_nodes)

    (filtered_graphml, filtered_pkl), save_filtered_sec = _timed_step(
        "Save LLM-filtered graph artifacts",
        lambda: _save_filtered_graph_artifacts(run_dir, selected_nodes, graph_edges),
    )
    print(f"[INFO] Saved filtered GraphML: {filtered_graphml}")
    print(f"[INFO] Saved filtered PKL: {filtered_pkl}")

    out_dir = run_dir / "multistream"
    builder = MultiStreamArtifactBuilder(data_dir=out_dir)
    manifest, build_sec = _timed_step(
        "Build multistream parquet artifacts",
        lambda: builder.build(anomaly, selected_nodes),
    )

    researcher = Phase3Researcher()
    _, ingest_sec = _timed_step(
        "Ingest cleaned/chunked data",
        lambda: researcher.ingest(anomaly, selected_nodes),
    )
    results, retrieve_sec = _timed_step(
        "Retrieve top context chunks",
        lambda: researcher.retrieve(f"drivers behind move in {anomaly['symbol']}"),
    )

    if not results:
        raise AssertionError("No retrieval results produced by Phase3Researcher")

    return {
        "run_dir": str(run_dir),
        "manifest": manifest,
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges),
        "selected_nodes": len(selected_nodes),
        "filtered_graphml": str(filtered_graphml),
        "filtered_pkl": str(filtered_pkl),
        "result_count": len(results),
        "timings_sec": {
            "load": round(load_sec, 3),
            "rank": round(rank_sec, 3),
            "save_filtered_graph": round(save_filtered_sec, 3),
            "build_artifacts": round(build_sec, 3),
            "ingest": round(ingest_sec, 3),
            "retrieve": round(retrieve_sec, 3),
        },
    }


def test_multistream_pipeline_from_signal_graph_outputs():
    """
    End-to-end bridge test:
    - consumes run artifacts from tests/test_signal_graph.py output layout
    - builds multi-stream parquet artifacts
    - runs ingestion + retrieval via Phase3Researcher
    - persists LLM-filtered subgraph in graphml + pkl files
    """
    run_id = os.getenv("RUN_ID")
    run_dir = Path("data") / run_id if run_id else _find_latest_run_dir(Path("data"))

    if run_dir is None or not run_dir.exists():
        raise AssertionError("No data/run_* found. Run tests/test_signal_graph.py first or set RUN_ID.")

    outcome = run_multistream_from_run_dir(run_dir)

    manifest_path = Path(outcome["manifest"].get("news_parquet", "")).parent / "manifest.json"
    assert manifest_path.exists(), "manifest.json should be generated in run_dir/multistream"
    assert outcome["result_count"] > 0
    assert Path(outcome["filtered_graphml"]).exists()
    assert Path(outcome["filtered_pkl"]).exists()


if __name__ == "__main__":
    run_id = os.getenv("RUN_ID")
    run_dir = Path("data") / run_id if run_id else _find_latest_run_dir(Path("data"))
    if run_dir is None:
        raise SystemExit("No data/run_* found. Run tests/test_signal_graph.py first or set RUN_ID.")

    out = run_multistream_from_run_dir(run_dir)
    print(json.dumps(out, indent=2))
