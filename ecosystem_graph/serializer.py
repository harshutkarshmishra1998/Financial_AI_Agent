import pandas as pd


def save_graph(nodes, edges, path="data/graph/"):
    node_df = pd.DataFrame([n.model_dump() for n in nodes])
    edge_df = pd.DataFrame([e.model_dump() for e in edges])

    node_df.to_parquet(path + "nodes.parquet")
    edge_df.to_parquet(path + "edges.parquet")