from __future__ import annotations

from pathlib import Path

from reasoning.data_loader import load_run_context
from reasoning.pipeline import _build_prompt, generate_anomaly_reasoning


def test_build_prompt_from_real_run_data_is_bounded() -> None:
    run_dir = Path("data/run_1462fceff3c4")
    context = load_run_context(run_dir)

    prompt = _build_prompt(context)

    assert isinstance(prompt, str)
    assert len(prompt) <= 16_050
    assert "Latest anomaly:" in prompt


def test_generate_anomaly_reasoning_from_existing_run_dir() -> None:
    run_dir = Path("data/run_1462fceff3c4")
    result = generate_anomaly_reasoning(run_dir)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


if __name__ == "__main__":
    test_build_prompt_from_real_run_data_is_bounded()
    test_generate_anomaly_reasoning_from_existing_run_dir()
    print("All reasoning pipeline tests passed.")
