from __future__ import annotations

import json
from pathlib import Path

from .data_loader import load_run_context
from .llm_client import generate_reasoning_text


def _build_prompt(context: dict) -> str:
    anomaly = context.get("latest_anomaly", {}) or {}

    return (
        "You are given outputs from a financial anomaly detection run. "
        "Explain the most likely reason the anomaly happened.\n\n"
        f"Latest anomaly:\n{json.dumps(anomaly, indent=2, default=str)}\n\n"
        f"Graph summary:\n{json.dumps(context.get('graph', {}), indent=2, default=str)}\n\n"
        f"Multistream manifest:\n{json.dumps(context.get('manifest', {}), indent=2, default=str)}\n\n"
        f"News sample:\n{json.dumps(context.get('news_sample', []), indent=2, default=str)}\n\n"
        f"Macro sample:\n{json.dumps(context.get('macro_sample', []), indent=2, default=str)}\n\n"
        f"Stock sample:\n{json.dumps(context.get('stock_sample', []), indent=2, default=str)}\n\n"
        "Response format:\n"
        "1) Primary cause hypothesis\n"
        "2) Supporting evidence from artifacts\n"
        "3) Confidence level (low/medium/high)\n"
        "4) What additional data would validate this hypothesis"
    )


def generate_anomaly_reasoning(run_directory: str | Path) -> str:
    """
    Public module entrypoint.
    Accepts a run directory (e.g. data/run_<id>) and returns a reasoned response.
    """
    context = load_run_context(run_directory)
    prompt = _build_prompt(context)
    return generate_reasoning_text(prompt=prompt, context=context)
