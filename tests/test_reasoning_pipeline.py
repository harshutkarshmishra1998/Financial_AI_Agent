from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from reasoning.llm_client import generate_reasoning_text
from reasoning.pipeline import _build_prompt, generate_anomaly_reasoning


def test_build_prompt_truncates_large_context() -> None:
    very_long_text = "market_event_" * 10_000
    context = {
        "latest_anomaly": {"metric": "spread", "details": very_long_text},
        "graph": {"nodes": [f"n{i}" for i in range(1000)]},
        "manifest": {"feeds": ["news", "macro", "stock"]},
        "news_sample": [{"headline": very_long_text}],
        "macro_sample": [{"series": "CPI", "commentary": very_long_text}],
        "stock_sample": [{"ticker": "AAPL", "notes": very_long_text}],
    }

    prompt = _build_prompt(context)

    assert len(prompt) <= 16_050
    assert "[truncated" in prompt


def test_generate_reasoning_text_falls_back_on_llm_error() -> None:
    context = {
        "latest_anomaly": {"metric": "volatility", "timestamp": "2026-01-01", "anomaly_score": 0.91},
        "graph": {"node_count": 11, "edge_count": 15},
        "manifest": {"sources": ["news", "stock"]},
    }

    with patch("reasoning.llm_client._get_groq_client", side_effect=RuntimeError("boom")):
        result = generate_reasoning_text(prompt="analyze", context=context)

    assert "deterministic fallback" in result
    assert "volatility" in result


def test_generate_anomaly_reasoning_from_existing_run_dir() -> None:
    run_dir = Path("data/run_1462fceff3c4")
    with patch(
        "reasoning.pipeline.generate_reasoning_text",
        return_value="mocked response",
    ) as mocked:
        result = generate_anomaly_reasoning(run_dir)

    assert result == "mocked response"
    mocked.assert_called_once()


if __name__ == "__main__":
    test_build_prompt_truncates_large_context()
    test_generate_reasoning_text_falls_back_on_llm_error()
    test_generate_anomaly_reasoning_from_existing_run_dir()
    print("All reasoning pipeline tests passed.")
