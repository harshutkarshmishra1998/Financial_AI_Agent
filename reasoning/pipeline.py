# reasoning/pipeline.py

from pathlib import Path
from .context import load_run_context
from .features import (
    extract_graph_features,
    summarize_stock,
    summarize_macro,
    summarize_news,
)
from .prompt_builder import build_prompt
from .llm_interface import generate_reasoning_text


def generate_anomaly_reasoning(run_dir: Path) -> str:
    ctx = load_run_context(run_dir)

    graph_features = extract_graph_features(
        ctx.graph,
        ctx.anomaly["symbol"]
    )

    # stock_summary = summarize_stock(ctx.stock_df)
    # macro_summary = summarize_macro(ctx.macro_df)
    # news_summary = summarize_news(ctx.news_df)
    import pandas as pd

    stock_summary = summarize_stock(pd.DataFrame(ctx.stock))
    macro_summary = summarize_macro(pd.DataFrame(ctx.macro))
    news_summary = summarize_news(pd.DataFrame(ctx.news))

    prompt = build_prompt(
        ctx.anomaly,
        graph_features,
        stock_summary,
        macro_summary,
        news_summary,
    )

    return generate_reasoning_text(prompt)