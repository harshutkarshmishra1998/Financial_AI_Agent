from __future__ import annotations

import json
from pathlib import Path

from reasoning.pipeline import generate_anomaly_reasoning


def test_generate_anomaly_reasoning_from_existing_run_dir() -> None:
    run_dir = Path("data/run_1462fceff3c4")
    result = generate_anomaly_reasoning(run_dir)

    assert isinstance(result, str)
    assert result
    assert "RELIANCE.NS" in result


def test_generate_anomaly_reasoning_with_json_fallback_parquet(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_test"
    (run_dir / "signal").mkdir(parents=True)
    (run_dir / "multistream").mkdir(parents=True)

    (run_dir / "signal" / "anomalies.jsonl").write_text(
        '{"symbol":"ABC.NS","event_timestamp":"2024-01-01","price_change_pct":5.1}\n',
        encoding="utf-8",
    )

    for name in ["news", "macro", "stock"]:
        (run_dir / "multistream" / f"{name}.parquet").write_text(
            json.dumps([{"graph_node": "oil", "content": "sample"}]),
            encoding="utf-8",
        )

    (run_dir / "multistream" / "manifest.json").write_text(
        json.dumps({"rows": {"news": 1, "macro": 1, "stock": 1}}),
        encoding="utf-8",
    )

    result = generate_anomaly_reasoning(run_dir)

    assert "ABC.NS" in result
    assert "Most likely drivers" in result
