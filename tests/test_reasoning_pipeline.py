from __future__ import annotations

import json
from pathlib import Path

from reasoning.pipeline import generate_anomaly_reasoning


def test_generate_anomaly_reasoning_from_existing_run_dir() -> None:
    run_dir = Path("data/run_1462fceff3c4")
    result = generate_anomaly_reasoning(run_dir)

    print("Generated reasoning response:")
    print(result)


if __name__ == "__main__":
    test_generate_anomaly_reasoning_from_existing_run_dir()
