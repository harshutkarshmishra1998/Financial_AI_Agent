from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

import faiss
import pandas as pd

from multistream_researcher.embeddings.embedder import Embedder
from multistream_researcher.macro_connectors.world_bank import fetch_world_bank
from multistream_researcher.news_connectors.web_connector import search_and_load


def _safe_write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write parquet if engine exists, otherwise write JSON content to .parquet path."""
    try:
        df.to_parquet(path, index=False)
    except Exception:
        path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")
        path.with_suffix(path.suffix + ".format.txt").write_text(
            "Fallback JSON content stored with .parquet extension because parquet engine is unavailable.",
            encoding="utf-8",
        )


def _keywords_to_indicator(node: str) -> str | None:
    n = node.lower()
    mapping = {
        "oil": "NY.GDP.MKTP.KD.ZG",
        "inflation": "FP.CPI.TOTL.ZG",
        "repo": "FR.INR.RINR",
        "rate": "FR.INR.RINR",
        "usd": "PA.NUS.FCRF",
        "tax": "GC.TAX.TOTL.GD.ZS",
    }
    for k, indicator in mapping.items():
        if k in n:
            return indicator
    return None


def _extract_symbols(graph_nodes: Iterable[str], anomaly_symbol: str | None = None) -> list[str]:
    symbols: list[str] = []
    pattern = re.compile(r"\b[A-Z]{2,10}(?:\.[A-Z]{1,4})?\b")
    for node in graph_nodes:
        for match in pattern.findall(node):
            if anomaly_symbol and match == anomaly_symbol:
                continue
            if match not in symbols:
                symbols.append(match)
    return symbols


def _synthetic_price(symbol: str) -> dict:
    seed = int(hashlib.sha256(symbol.encode("utf-8")).hexdigest()[:8], 16)
    close = round(50 + (seed % 5000) / 100, 2)
    open_ = round(close * 0.99, 2)
    high = round(close * 1.02, 2)
    low = round(close * 0.98, 2)
    volume = (seed % 9000000) + 100000
    return {"open": open_, "high": high, "low": low, "close": close, "volume": volume}


class MultiStreamArtifactBuilder:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.embedder = Embedder()

    def _build_news_df(self, anomaly_event: dict, graph_nodes: list[str]) -> pd.DataFrame:
        rows = []
        for node in graph_nodes:
            query = f"{node} {anomaly_event.get('timestamp', '')[:7]} market news"
            docs = search_and_load(query, max_results=3)
            if not docs:
                rows.append(
                    {
                        "graph_node": node,
                        "query": query,
                        "content": f"No live news found for {node}.",
                        "url": None,
                        "source": "fallback",
                    }
                )
                continue
            for d in docs:
                rows.append(
                    {
                        "graph_node": node,
                        "query": query,
                        "content": d.get("content", ""),
                        "url": d.get("url"),
                        "source": "web",
                    }
                )
        return pd.DataFrame(rows)

    def _build_macro_df(self, graph_nodes: list[str]) -> pd.DataFrame:
        rows = []
        for node in graph_nodes:
            indicator = _keywords_to_indicator(node)
            if not indicator:
                rows.append(
                    {
                        "graph_node": node,
                        "indicator": None,
                        "value": None,
                        "date": None,
                        "source": "fallback",
                        "content": f"No macro indicator mapping for node: {node}",
                    }
                )
                continue

            try:
                payload = fetch_world_bank(indicator)
                observations = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
                latest = next((x for x in observations if x and x.get("value") is not None), None)
                if latest is None:
                    raise ValueError("No values returned")
                rows.append(
                    {
                        "graph_node": node,
                        "indicator": indicator,
                        "value": latest.get("value"),
                        "date": latest.get("date"),
                        "source": "world_bank",
                        "content": f"{node} indicator {indicator} value {latest.get('value')} on {latest.get('date')}",
                    }
                )
            except Exception:
                rows.append(
                    {
                        "graph_node": node,
                        "indicator": indicator,
                        "value": None,
                        "date": None,
                        "source": "fallback",
                        "content": f"Macro data unavailable for node: {node} ({indicator})",
                    }
                )
        return pd.DataFrame(rows)

    def _build_stock_df(self, anomaly_event: dict, graph_nodes: list[str]) -> pd.DataFrame:
        symbols = _extract_symbols(graph_nodes, anomaly_event.get("symbol"))
        if not symbols:
            symbols = [f"NODE_{i+1}" for i in range(len(graph_nodes))]

        rows = []
        for symbol in symbols:
            px = _synthetic_price(symbol)
            rows.append(
                {
                    "symbol": symbol,
                    "source": "synthetic_from_graph_node",
                    **px,
                    "content": (
                        f"{symbol} open {px['open']} high {px['high']} low {px['low']} "
                        f"close {px['close']} volume {px['volume']}"
                    ),
                }
            )
        return pd.DataFrame(rows)

    def _build_faiss(self, df: pd.DataFrame, text_col: str, stem: str) -> Path:
        texts = [str(x) for x in df[text_col].fillna("").tolist()]
        vectors = self.embedder.encode(texts)
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        out_path = self.data_dir / f"{stem}.faiss"
        faiss.write_index(index, str(out_path))
        return out_path

    def build(self, anomaly_event: dict, graph_nodes: list[str]) -> dict:
        news_df = self._build_news_df(anomaly_event, graph_nodes)
        macro_df = self._build_macro_df(graph_nodes)
        stock_df = self._build_stock_df(anomaly_event, graph_nodes)

        news_path = self.data_dir / "news.parquet"
        macro_path = self.data_dir / "macro.parquet"
        stock_path = self.data_dir / "stock.parquet"

        _safe_write_parquet(news_df, news_path)
        _safe_write_parquet(macro_df, macro_path)
        _safe_write_parquet(stock_df, stock_path)

        news_faiss = self._build_faiss(news_df, "content", "news")
        macro_faiss = self._build_faiss(macro_df, "content", "macro")
        stock_faiss = self._build_faiss(stock_df, "content", "stock")

        manifest = {
            "news_parquet": str(news_path),
            "macro_parquet": str(macro_path),
            "stock_parquet": str(stock_path),
            "news_faiss": str(news_faiss),
            "macro_faiss": str(macro_faiss),
            "stock_faiss": str(stock_faiss),
            "rows": {
                "news": len(news_df),
                "macro": len(macro_df),
                "stock": len(stock_df),
            },
        }
        (self.data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
