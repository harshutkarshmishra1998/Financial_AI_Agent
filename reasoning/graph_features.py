# reasoning/graph_features.py

from __future__ import annotations
import networkx as nx
from typing import Dict, List


def extract_structural_features(graph: nx.DiGraph, symbol: str) -> Dict:
    if symbol not in graph.nodes:
        raise ValueError(f"Symbol {symbol} not found in graph.")

    # First-degree neighbors
    out_edges = list(graph.out_edges(symbol, data=True))
    in_edges = list(graph.in_edges(symbol, data=True))

    direct_influences = []
    exposures = []

    for _, target, data in out_edges:
        direct_influences.append({
            "node": target,
            "relation": data.get("relation", "unknown"),
            "weight": float(data.get("weight", 1.0)),
        })

    for source, _, data in in_edges:
        exposures.append({
            "node": source,
            "relation": data.get("relation", "unknown"),
            "weight": float(data.get("weight", 1.0)),
        })

    # Centrality
    degree_centrality = nx.degree_centrality(graph).get(symbol, 0.0)
    pagerank = nx.pagerank(graph).get(symbol, 0.0)

    return {
        "symbol": symbol,
        "degree_centrality": degree_centrality,
        "pagerank": pagerank,
        "direct_influences": sorted(
            direct_influences,
            key=lambda x: x["weight"],
            reverse=True
        )[:5],
        "exposures": sorted(
            exposures,
            key=lambda x: x["weight"],
            reverse=True
        )[:5],
    }