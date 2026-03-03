from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .data_loader import load_run_context
from .llm_client import generate_reasoning_text


_MAX_PROMPT_CHARS = 16_000
_MAX_FIELD_CHARS = 360


def _truncate_value(value: Any) -> Any:
    if isinstance(value, str):
        if len(value) <= _MAX_FIELD_CHARS:
            return value
        return f"{value[:_MAX_FIELD_CHARS]}... [truncated {len(value) - _MAX_FIELD_CHARS} chars]"

    if isinstance(value, list):
        return [_truncate_value(item) for item in value]

    if isinstance(value, dict):
        return {str(k): _truncate_value(v) for k, v in value.items()}

    return value


def _json_block(title: str, payload: Any) -> str:
    compact_payload = _truncate_value(payload)
    return f"{title}:\n{json.dumps(compact_payload, indent=2, default=str)}\n\n"


def _build_prompt(context: dict) -> str:
    sections = [
        "You are given outputs from a financial anomaly detection run. Explain the most likely reason the anomaly happened.\n\n",
        _json_block("Latest anomaly", context.get("latest_anomaly", {}) or {}),
        _json_block("Graph summary", context.get("graph", {})),
        _json_block("Multistream manifest", context.get("manifest", {})),
        _json_block("News sample", context.get("news_sample", [])),
        _json_block("Macro sample", context.get("macro_sample", [])),
        _json_block("Stock sample", context.get("stock_sample", [])),
        (
            "Response format:\n"
            "1) Primary cause hypothesis\n"
            "2) Supporting evidence from artifacts\n"
            "3) Confidence level (low/medium/high)\n"
            "4) What additional data would validate this hypothesis"
        ),
    ]

    prompt = ""
    for section in sections:
        candidate = f"{prompt}{section}"
        if len(candidate) > _MAX_PROMPT_CHARS:
            remaining = _MAX_PROMPT_CHARS - len(prompt)
            if remaining > 0:
                prompt += f"{section[:remaining]}\n\n[Prompt truncated to fit token limits.]"
            else:
                prompt += "\n\n[Prompt truncated to fit token limits.]"
            break
        prompt = candidate

    return prompt


def generate_anomaly_reasoning(run_directory: str | Path) -> str:
    """
    Public module entrypoint.
    Accepts a run directory (e.g. data/run_<id>) and returns a reasoned response.
    """
    context = load_run_context(run_directory)
    prompt = _build_prompt(context)
    return generate_reasoning_text(prompt=prompt, context=context)
