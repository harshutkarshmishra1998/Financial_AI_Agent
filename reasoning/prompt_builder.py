import json

MAX_PROMPT_CHARS = 14000


def build_prompt(anomaly, graph_features, stock_summary, macro_summary, news_summary):

    system_rules = """
You are a structural financial reasoning engine.

Rules:
- Use ONLY provided structured inputs.
- Do NOT introduce external macro assumptions.
- Rank top 3 structural drivers.
- Separate:
    1. Graph-structural drivers
    2. Regime (stock/macro) alignment
    3. News alignment
- Provide confidence score (0–1).
- If evidence is weak, say so explicitly. Give me the 
"""

    payload = {
        "anomaly": anomaly,
        "graph_features": graph_features,
        "stock_summary": stock_summary,
        "macro_summary": macro_summary,
        "news_summary": news_summary,
    }

    prompt = system_rules + "\n\nINPUT DATA:\n" + json.dumps(payload, indent=2)

    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError("Prompt too large.")

    return prompt