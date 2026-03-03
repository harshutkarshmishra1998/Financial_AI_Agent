from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def _read_table(path: Path) -> pd.DataFrame:
    """
    Read a tabular artifact with graceful fallback.

    Supports:
    - JSONL
    - Parquet (when parquet engine is available)
    - JSON payload saved in .parquet fallback files
    """
    if not path.exists():
        return pd.DataFrame()

    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        try:
            return pd.read_json(path, lines=True)
        except Exception:
            return pd.DataFrame()

    if suffix == ".parquet":
        try:
            return pd.read_parquet(path)
        except Exception:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    return pd.DataFrame(payload)
            except Exception:
                return pd.DataFrame()

    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return pd.DataFrame(payload)
            if isinstance(payload, dict):
                return pd.DataFrame([payload])
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def _safe_head(df: pd.DataFrame, max_rows: int = 8) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return df.head(max_rows).to_dict(orient="records") #type: ignore


def load_run_context(run_directory: str | Path) -> dict[str, Any]:
    run_dir = Path(run_directory)

    anomalies = _read_table(run_dir / "signal" / "anomalies.jsonl")
    signal_timeline = _read_table(run_dir / "signal" / "signal_timeline.jsonl")

    manifest_path = run_dir / "multistream" / "manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}

    multistream_dir = run_dir / "multistream"
    news = _read_table(multistream_dir / "news.parquet")
    macro = _read_table(multistream_dir / "macro.parquet")
    stock = _read_table(multistream_dir / "stock.parquet")

    graph_summary: dict[str, Any] = {}
    graphml_path = run_dir / "ecosystem_graph_filtered_llm.graphml"
    if not graphml_path.exists():
        graphml_path = run_dir / "ecosystem_graph.graphml"

    if graphml_path.exists():
        try:
            import networkx as nx

            graph = nx.read_graphml(graphml_path)
            graph_summary = {
                "graph_file": str(graphml_path),
                "node_count": int(graph.number_of_nodes()),
                "edge_count": int(graph.number_of_edges()),
                "sample_nodes": list(graph.nodes())[:12],
            }
        except Exception:
            graph_summary = {"graph_file": str(graphml_path), "error": "Unable to parse graph artifact."}

    latest_anomaly = anomalies.iloc[-1].to_dict() if not anomalies.empty else {}

    return {
        "run_directory": str(run_dir),
        "latest_anomaly": latest_anomaly,
        "anomaly_count": len(anomalies),
        "signal_timeline_sample": _safe_head(signal_timeline),
        "news_sample": _safe_head(news),
        "macro_sample": _safe_head(macro),
        "stock_sample": _safe_head(stock),
        "manifest": manifest,
        "graph": graph_summary,
    }
