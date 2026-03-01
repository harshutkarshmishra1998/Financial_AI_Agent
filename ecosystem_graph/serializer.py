from pathlib import Path

import pandas as pd


def save_graph(nodes, edges, path="data/graph/"):
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)

    node_df = pd.DataFrame([n.model_dump() for n in nodes])
    edge_df = pd.DataFrame([e.model_dump() for e in edges])

    node_df.to_parquet(output / "nodes.parquet", index=False)
    edge_df.to_parquet(output / "edges.parquet", index=False)
