from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _normalize_nodes_for_parquet(node_df: pd.DataFrame) -> pd.DataFrame:
    """
    PyArrow cannot serialize an all-empty dict column as struct with no children.
    Store metadata as JSON text for stable cross-platform parquet writes.
    """
    if "metadata" in node_df.columns:
        node_df = node_df.copy()

        def _to_json(value):
            if isinstance(value, dict):
                return json.dumps(value, sort_keys=True)
            if value is None:
                return "{}"
            return json.dumps(value)

        node_df["metadata"] = node_df["metadata"].apply(_to_json)

    return node_df


def save_graph(nodes, edges, path="data/graph/"):
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)

    node_df = pd.DataFrame([n.model_dump() for n in nodes])
    edge_df = pd.DataFrame([e.model_dump() for e in edges])

    node_df = _normalize_nodes_for_parquet(node_df)

    node_df.to_parquet(output / "nodes.parquet", index=False)
    edge_df.to_parquet(output / "edges.parquet", index=False)
