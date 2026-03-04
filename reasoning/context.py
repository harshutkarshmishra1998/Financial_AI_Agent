# reasoning/context.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import jsonlines
import pandas as pd
import networkx as nx


@dataclass
class RunContext:
    run_dir: Path
    anomaly: dict
    graph: nx.DiGraph
    stock: list[dict]
    macro: list[dict]
    news: list[dict]
    manifest: dict


def _load_anomaly(run_dir: Path) -> dict:
    path = run_dir / "signal" / "anomalies.jsonl"

    anomalies = []
    with jsonlines.open(path) as reader:
        for row in reader:
            anomalies.append(row)

    if not anomalies:
        raise ValueError("No anomalies found.")

    return sorted(anomalies, key=lambda x: x["event_timestamp"])[-1]


def _load_graph(run_dir: Path) -> nx.DiGraph:
    graph_path = run_dir / "ecosystem_graph.graphml"

    if not graph_path.exists():
        raise FileNotFoundError(f"Missing graph: {graph_path}")

    return nx.read_graphml(graph_path)


def _extract_content_rows(df: pd.DataFrame, source: str) -> list[dict]:
    """
    Extracts structured objects from the 'content' column.
    Handles dict / JSON string safely.
    """

    if "content" not in df.columns:
        raise ValueError(f"{source} parquet missing 'content' column.")

    rows = []

    for item in df["content"]:
        if isinstance(item, dict):
            rows.append(item)

        elif isinstance(item, str):
            try:
                rows.append(json.loads(item))
            except json.JSONDecodeError:
                rows.append({"raw": item})

        else:
            rows.append({"value": item})

    return rows


def _load_multistream(run_dir: Path):
    base = run_dir / "multistream"

    stock_df = pd.read_parquet(base / "stock.parquet")
    macro_df = pd.read_parquet(base / "macro.parquet")
    news_df = pd.read_parquet(base / "news.parquet")

    stock = _extract_content_rows(stock_df, "stock")
    macro = _extract_content_rows(macro_df, "macro")
    news = _extract_content_rows(news_df, "news")

    return stock, macro, news


def _load_manifest(run_dir: Path):
    path = run_dir / "multistream" / "manifest.json"

    if not path.exists():
        raise FileNotFoundError("Missing multistream manifest.")

    return json.loads(path.read_text())


def load_run_context(run_dir: Path) -> RunContext:
    run_dir = run_dir.resolve()

    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    anomaly = _load_anomaly(run_dir)
    graph = _load_graph(run_dir)
    stock, macro, news = _load_multistream(run_dir)
    manifest = _load_manifest(run_dir)

    return RunContext(
        run_dir=run_dir,
        anomaly=anomaly,
        graph=graph,
        stock=stock,
        macro=macro,
        news=news,
        manifest=manifest,
    )