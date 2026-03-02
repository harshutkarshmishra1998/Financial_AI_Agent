import concurrent.futures
from pathlib import Path
import shutil
import pandas as pd
import networkx as nx

from foundation import RunManager
from market_signal.engine import run as run_signal_engine

from ecosystem_graph.pipeline import EcosystemPipeline
from ecosystem_graph.visualize_graph import draw_ecosystem_graph
from ecosystem_graph.save_graph import save_graph_structure

from multistream_researcher.controller import Phase3Researcher
from multistream_researcher.storage import MultiStreamArtifactBuilder


# ==============================
# CONFIG
# ==============================

TICKER = "RELIANCE.NS"
START_DATE = "2019-01-16"
END_DATE = "2019-02-19"
UNIVERSE_PATH = "universe/market_universe.parquet"
DATA_ROOT = Path("data")


# ==============================
# PIPELINE
# ==============================

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

def run_full_pipeline():

    clear_directory("data")

    DATA_ROOT.mkdir(exist_ok=True)

    run_id = RunManager.new_run()
    run_dir = DATA_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run ID → {run_id}")

    # ------------------------------------------------
    # PHASE 1 + PHASE 2 (parallel)
    # ------------------------------------------------
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

    # ------------------------------------------------
    # SAVE GRAPH
    # ------------------------------------------------
    draw_ecosystem_graph(
        nodes,
        edges,
        output_file=str(run_dir / "ecosystem_graph.html")
    )

    save_graph_structure(nodes, edges, run_dir)

    # ------------------------------------------------
    # LOAD ANOMALY FROM SIGNAL OUTPUT
    # ------------------------------------------------
    anomalies_path = run_dir / "signal" / "anomalies.jsonl"
    df = pd.read_json(anomalies_path, lines=True)

    if df.empty:
        raise RuntimeError("No anomaly events detected")

    last = df.iloc[-1]

    anomaly = {
        "timestamp": str(last["event_timestamp"]),
        "symbol": str(last["symbol"]),
    }

    # ------------------------------------------------
    # LOAD GRAPH STRUCTURE
    # ------------------------------------------------
    graph = nx.read_graphml(run_dir / "ecosystem_graph.graphml")
    graph_nodes = [str(n) for n in graph.nodes()]

    # ------------------------------------------------
    # PHASE 3 — MULTISTREAM RESEARCH
    # ------------------------------------------------
    multistream_dir = run_dir / "multistream"

    builder = MultiStreamArtifactBuilder(data_dir=multistream_dir)
    manifest = builder.build(anomaly, graph_nodes)

    researcher = Phase3Researcher()
    researcher.ingest(anomaly, graph_nodes)

    results = researcher.retrieve(
        f"drivers behind move in {anomaly['symbol']}"
    )

    if not results:
        raise RuntimeError("Phase3 produced no retrieval results")

    print("Retrieved context chunks:", len(results))

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "graph_nodes": len(graph_nodes),
        "retrieved_chunks": len(results),
        "manifest": manifest
    }


# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    out = run_full_pipeline()
    print("\nPIPELINE COMPLETE")
    for k, v in out.items():
        print(k, "→", v)