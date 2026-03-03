from __future__ import annotations

import os


def _rule_based_reasoning(context: dict) -> str:
    anomaly = context.get("latest_anomaly", {}) or {}
    symbol = anomaly.get("symbol", "Unknown symbol")
    ts = anomaly.get("event_timestamp", "Unknown date")
    move = anomaly.get("price_change_pct", "N/A")

    news_items = context.get("news_sample", []) or []
    macro_items = context.get("macro_sample", []) or []
    stock_items = context.get("stock_sample", []) or []

    clues: list[str] = []
    if news_items:
        first_news = news_items[0]
        clues.append(f"news flow around `{first_news.get('graph_node', 'market drivers')}`")
    if macro_items:
        first_macro = macro_items[0]
        clues.append(f"macro indicator signals linked to `{first_macro.get('graph_node', 'economy')}`")
    if stock_items:
        clues.append("cross-asset price behavior from peer symbols")

    if not clues:
        clues.append("limited context artifacts available in this run")

    return (
        f"Anomaly summary: {symbol} moved {move}% on {ts}. "
        f"Most likely drivers are {', '.join(clues)}. "
        "This explanation is generated via fallback reasoning because no LLM provider was configured."
    )


def generate_reasoning_text(prompt: str, context: dict, model: str = "gpt-4o-mini") -> str:
    """
    Generate reasoning with LLM if API key is available.
    Falls back to deterministic template reasoning otherwise.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _rule_based_reasoning(context)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a financial anomaly root-cause analyst."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else _rule_based_reasoning(context)
    except Exception:
        return _rule_based_reasoning(context)
