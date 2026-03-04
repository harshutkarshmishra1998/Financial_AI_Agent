import pickle
from pathlib import Path
import sys
import pandas as pd
from multistream_researcher.llm_driver_ranker import LLMDriverRanker
import networkx as nx

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from multistream_researcher.controller import Phase3Researcher
from multistream_researcher.storage.artifact_builder import MultiStreamArtifactBuilder


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

    graphml_path = run_dir / "graph_outputs/ecosystem_graph_filtered_llm.graphml"
    pkl_path = run_dir / "graph_outputs/ecosystem_graph_filtered_llm.pkl"

    nx.write_graphml(filtered_graph, graphml_path)
    with pkl_path.open("wb") as f:
        pickle.dump(filtered_graph, f)

    return graphml_path, pkl_path


def run_multistream_researcher(run_id):

    run_dir = Path("data") / run_id
    anomalies_path = run_dir / "signal" / "anomalies.jsonl"
    df = pd.read_json(anomalies_path, lines=True)

    anomaly = {
        "timestamp": str(df.iloc[-1]["event_timestamp"]),
        "symbol": str(df.iloc[-1]["symbol"]),
    }

    graph = nx.read_graphml(run_dir / "graph_outputs/ecosystem_graph.graphml")
    graph_nodes = [str(node) for node in graph.nodes()]

    ranker = LLMDriverRanker()
    selected_nodes = ranker.rank(anomaly, graph_nodes)
    if not selected_nodes:
        selected_nodes = graph_nodes[:8]

    _save_filtered_graph_artifacts(run_dir, selected_nodes, list(graph.edges()))

    multistream_dir = run_dir / "multistream"
    
    builder = MultiStreamArtifactBuilder(data_dir=multistream_dir)
    builder.build(anomaly, selected_nodes)

    agent = Phase3Researcher()
    agent.ingest(anomaly, selected_nodes)
