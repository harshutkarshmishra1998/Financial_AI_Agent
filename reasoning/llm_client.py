from __future__ import annotations

from importlib import import_module
from typing import Any



def _deterministic_fallback(context: dict[str, Any], error_message: str | None = None) -> str:
    anomaly = context.get("latest_anomaly", {}) or {}
    metric = anomaly.get("metric", "unknown metric")
    timestamp = anomaly.get("timestamp", "unknown time")
    score = anomaly.get("anomaly_score", anomaly.get("score", "unknown score"))

    header = "Using deterministic fallback reasoning"
    if error_message:
        header = f"{header} (LLM request issue: {error_message})"

    return (
        f"{header}.\n\n"
        "1) Primary cause hypothesis\n"
        f"The anomaly in {metric} around {timestamp} may be linked to a sudden market-moving event or data regime shift.\n\n"
        "2) Supporting evidence from artifacts\n"
        f"- Reported anomaly score: {score}\n"
        f"- Available graph stats: {context.get('graph', {})}\n"
        f"- Data feeds included in manifest: {context.get('manifest', {})}\n\n"
        "3) Confidence level\n"
        "medium\n\n"
        "4) What additional data would validate this hypothesis\n"
        "- More recent high-frequency market and macro observations around the anomaly window\n"
        "- Event-aligned news summaries for impacted entities\n"
        "- Peer asset movement comparison to separate idiosyncratic vs market-wide effects"
    )


def _get_groq_client() -> Any:
    groq_module = import_module("groq")
    return groq_module.Groq()


def generate_reasoning_text(prompt: str, context: dict, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Generate reasoning with LLM if API key is available.
    Falls back to deterministic template reasoning otherwise.
    """

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a financial anomaly root-cause analyst."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            return _deterministic_fallback(context=context, error_message="empty LLM response")
        return content.strip() #type: ignore
    except Exception as exc:
        return _deterministic_fallback(context=context, error_message=str(exc))
