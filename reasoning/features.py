import networkx as nx


def extract_graph_features(graph: nx.DiGraph, symbol: str):
    if symbol not in graph:
        raise ValueError(f"{symbol} not in graph.")

    out_edges = list(graph.out_edges(symbol, data=True))
    in_edges = list(graph.in_edges(symbol, data=True))

    return {
        "degree_centrality": nx.degree_centrality(graph).get(symbol, 0),
        "pagerank": nx.pagerank(graph).get(symbol, 0),
        "out_edges": [
            {"to": t, **d} for _, t, d in out_edges
        ],
        "in_edges": [
            {"from": s, **d} for s, _, d in in_edges
        ],
    }


def summarize_stock(df):
    if df.empty:
        return {}

    summary = {}

    for col in df.columns:
        if df[col].dtype.kind in "fi":
            summary[col] = {
                "mean": float(df[col].mean()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }

    return summary


def summarize_macro(df):
    if df.empty:
        return {}

    summary = {}

    for col in df.columns:
        if df[col].dtype.kind in "fi":
            summary[col] = {
                "mean": float(df[col].mean()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }

    return summary


def summarize_news(df):
    if df.empty:
        return {}

    summary = {
        "row_count": len(df)
    }

    for col in df.columns:
        if df[col].dtype.kind in "fi":
            summary[col] = {
                "mean": float(df[col].mean())
            }

    return summary