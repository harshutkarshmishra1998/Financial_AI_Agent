from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from foundation import ArtifactStore, RunManager
from market_signal import engine as signal_engine
from ecosystem_graph.data_interface import TimeSeriesProvider
from ecosystem_graph.governance import ExpansionController
from ecosystem_graph.llm_interface import GroqLLM
from ecosystem_graph.runner import run as run_ecosystem
from ecosystem_graph.validation import StatisticalValidator


def _mock_ohlcv() -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=90, freq="D")
    base = np.linspace(100, 112, len(idx))
    close = base.copy()
    close[40] = close[39] * 1.14
    close[41:] = close[41:] + 10
    volume = np.full(len(idx), 1_000_000)
    volume[40] = 2_500_000

    df = pd.DataFrame(
        {
            "open": close * 0.99,
            "high": close * 1.01,
            "low": close * 0.98,
            "close": close,
            "volume": volume,
        },
        index=idx,
    )
    df.index.name = "date"
    return df


def _series(seed: int) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=240, freq="D")
    trend = np.linspace(0, 2, len(idx))
    return pd.Series(100 + trend + rng.normal(0, 0.2, len(idx)), index=idx)


class StubLLM(GroqLLM):
    def propose_related_factors(self, node_name: str, context=None):
        return [
            {"name": "Refining Margin", "type": "factor", "relationship": "influenced_by"},
        ]


def test_foundation_to_market_signal_to_ecosystem_pipeline(monkeypatch):
    data_dir = Path("data")
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(signal_engine, "fetch_ohlcv", lambda *args, **kwargs: _mock_ohlcv())
    monkeypatch.setattr(signal_engine, "rolling_dtw", lambda _df: np.zeros(len(_df) - 5))

    run_id = RunManager.new_run()
    events = signal_engine.run("OILCO", "2024-01-01", "2024-04-01", run_id)
    assert len(events) >= 1

    stored = ArtifactStore.read(run_id, "signal", "anomalies", type(events[0]))
    assert len(stored) == len(events)

    company_map = {
        "OILCO": {
            "company_name": "Oil Company A",
            "sector": "Energy",
            "inputs": [{"name": "Brent crude"}],
            "outputs": [{"name": "Diesel"}],
            "competitors": ["OILCO_B"],
            "input_dependencies": {
                "Brent crude": {
                    "producers": ["Producer P"],
                    "competing_materials": ["Competing Material Z"],
                    "influenced_by": ["USD/INR", "Import/export duties", "OPEC production decisions"],
                }
            },
            "output_dependencies": {
                "Diesel": {
                    "consumer_sectors": ["Transport"],
                    "competing_products": ["EV Mobility"],
                    "influenced_by": ["GDP Growth", "Liquidity surplus/deficit"],
                }
            },
        },
        "OILCO_B": {
            "company_name": "Oil Company B",
            "sector": "Energy",
            "inputs": [{"name": "Brent crude"}],
            "outputs": [{"name": "Petrol"}],
            "competitors": [],
            "input_dependencies": {
                "Brent crude": {
                    "producers": ["Producer P"],
                    "competing_materials": ["Competing Material Z"],
                    "influenced_by": ["USD/INR"],
                }
            },
            "output_dependencies": {
                "Petrol": {
                    "consumer_sectors": ["Retail Fuel"],
                    "competing_products": ["EV Mobility"],
                    "influenced_by": ["GDP Growth"],
                }
            },
        },
    }

    series_map = {
        "Oil Company A": _series(1),
        "Oil Company B": _series(2),
        "Brent crude": _series(3),
        "USD/INR": _series(4),
        "Import/export duties": _series(5),
        "OPEC production decisions": _series(6),
        "Diesel": _series(7),
        "GDP Growth": _series(8),
        "Liquidity surplus/deficit": _series(9),
        "Refining Margin": _series(10),
    }

    provider = TimeSeriesProvider(company_map=company_map, series_map=series_map)

    nodes, edges = run_ecosystem(
        "OILCO",
        data_provider=provider,
        llm=StubLLM(),
        validator=StatisticalValidator(corr_threshold=0.05),
        controller=ExpansionController(max_nodes=200, max_depth=3, competitor_limit=3),
    )

    node_names = {n.name for n in nodes}
    edge_tuples = {(e.source_node_id, e.target_node_id, e.relationship_type) for e in edges}

    assert "Brent crude" in node_names
    assert "USD/INR" in node_names
    assert "Import/export duties" in node_names
    assert "Diesel" in node_names
    assert "Transport" in node_names
    assert "OPEC production decisions" in node_names

    input_id = "input:brent crude"
    output_id = "output:diesel"
    company_id = "company:oil company a"

    assert (company_id, input_id, "depends_on") in edge_tuples
    assert ("macro:usd/inr", input_id, "influenced_by") in edge_tuples
    assert (company_id, output_id, "produces") in edge_tuples
    assert ("macro:gdp growth", output_id, "influenced_by") in edge_tuples

    # expandable company logic: competitor company should also get its own dependency expansion
    assert "Petrol" in node_names
