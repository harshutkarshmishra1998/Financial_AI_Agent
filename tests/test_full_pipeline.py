import concurrent.futures
from pathlib import Path
import shutil
import time
import pickle
import pandas as pd
import networkx as nx

from foundation import RunManager
from market_signal.engine import run as run_signal_engine

from ecosystem_graph.pipeline import EcosystemPipeline
from ecosystem_graph.visualize_graph import draw_ecosystem_graph
from ecosystem_graph.save_graph import save_graph_structure

from multistream_researcher.controller import Phase3Researcher
from multistream_researcher.llm_driver_ranker import LLMDriverRanker
from multistream_researcher.storage import MultiStreamArtifactBuilder


TICKER = "RELIANCE.NS"
START_DATE = "2019-01-16"
END_DATE = "2019-02-19"
UNIVERSE_PATH = "universe/market_universe.parquet"
DATA_ROOT = Path("data")


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


def _timed_step(label: str, fn):
    start = time.perf_counter()
    print(f"\n[START] {label}")
    value = fn()
    elapsed = time.perf_counter() - start
    print(f"[DONE]  {label} ({elapsed:.2f}s)")
    return value, elapsed




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


def run_full_pipeline():

    DATA_ROOT.mkdir(exist_ok=True)

    run_id = RunManager.new_run()
    run_dir = DATA_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run ID → {run_id}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

        signal_start = time.perf_counter()
        f_signal = executor.submit(
            run_signal_engine,
            symbol=TICKER,
            start=START_DATE,
            end=END_DATE,
            run_id=run_id,
        )

        graph_start = time.perf_counter()
        f_graph = executor.submit(lambda: EcosystemPipeline(UNIVERSE_PATH).run(TICKER))

        _events = f_signal.result()
        signal_elapsed = time.perf_counter() - signal_start
        print(f"[DONE]  Signal engine ({signal_elapsed:.2f}s)")

        nodes, edges = f_graph.result()
        graph_elapsed = time.perf_counter() - graph_start
        print(f"[DONE]  Ecosystem graph generation ({graph_elapsed:.2f}s)")

    _, draw_sec = _timed_step(
        "Draw and save ecosystem graph HTML",
        lambda: draw_ecosystem_graph(nodes, edges, output_file=str(run_dir / "ecosystem_graph.html")),
    )

    _, struct_sec = _timed_step(
        "Save graph structure files",
        lambda: save_graph_structure(nodes, edges, run_dir),
    )

    anomalies_path = run_dir / "signal" / "anomalies.jsonl"
    df, anomaly_sec = _timed_step(
        "Load anomalies",
        lambda: pd.read_json(anomalies_path, lines=True),
    )

    if df.empty:
        raise RuntimeError("No anomaly events detected")

    last = df.iloc[-1]

    anomaly = {
        "timestamp": str(last["event_timestamp"]),
        "symbol": str(last["symbol"]),
    }

    graph, graph_load_sec = _timed_step(
        "Load graph structure",
        lambda: nx.read_graphml(run_dir / "ecosystem_graph.graphml"),
    )
    graph_nodes = [str(node) for node in graph.nodes()]

    ranker = LLMDriverRanker()
    selected_nodes, rank_sec = _timed_step(
        "LLM node filtering",
        lambda: ranker.rank(anomaly, graph_nodes),
    )
    if not selected_nodes:
        selected_nodes = graph_nodes[:8]

    print(
        "[INFO] Node counts before multistream researcher → "
        f"original: {len(graph_nodes)}, after LLM filter: {len(selected_nodes)}"
    )
    print("[INFO] Original nodes:")
    print(graph_nodes)
    print("[INFO] LLM-filtered nodes:")
    print(selected_nodes)

    (filtered_graph_paths, save_filtered_sec) = _timed_step(
        "Save LLM-filtered graph artifacts",
        lambda: _save_filtered_graph_artifacts(run_dir, selected_nodes, list(graph.edges())),
    )
    filtered_graphml, filtered_pkl = filtered_graph_paths
    print(f"[INFO] Saved filtered GraphML: {filtered_graphml}")
    print(f"[INFO] Saved filtered PKL: {filtered_pkl}")

    multistream_dir = run_dir / "multistream"

    builder = MultiStreamArtifactBuilder(data_dir=multistream_dir)
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
        raise RuntimeError("Phase3 produced no retrieval results")

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "graph_nodes": len(graph_nodes),
        "selected_nodes": len(selected_nodes),
        "retrieved_chunks": len(results),
        "filtered_graphml": str(filtered_graphml),
        "filtered_pkl": str(filtered_pkl),
        "timings_sec": {
            "signal": round(signal_elapsed, 3),
            "graph_generation": round(graph_elapsed, 3),
            "draw_graph": round(draw_sec, 3),
            "save_graph_files": round(struct_sec, 3),
            "load_anomalies": round(anomaly_sec, 3),
            "load_graph": round(graph_load_sec, 3),
            "llm_filter": round(rank_sec, 3),
            "save_filtered_graph": round(save_filtered_sec, 3),
            "build_artifacts": round(build_sec, 3),
            "ingest": round(ingest_sec, 3),
            "retrieve": round(retrieve_sec, 3),
        },
        "manifest": manifest,
    }


if __name__ == "__main__":
    out = run_full_pipeline()
    print("\nPIPELINE COMPLETE")
    print(out)
