from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from foundation import ArtifactStore, RunManager
from market_signal import engine as signal_engine
from ecosystem_graph.data_interface import LLMDrivenEconomicProvider
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
    def __init__(self):
        pass

    def propose_related_factors(self, node_name: str, context=None):
        return [{"name": "Refining Margin", "type": "factor", "relationship": "influenced_by"}]

    def extract_company_profile(self, symbol: str, company_name: str, sector: str):
        return {
            "inputs": [{"name": "Brent crude"}],
            "outputs": [{"name": "Diesel"}],
            "competitors": ["OILCO_B"],
            "input_dependencies": {
                "Brent crude": {
                    "producers": ["Producer P"],
                    "competing_materials": ["Competing Material Z"],
                    "influenced_by": ["USD/INR", "OPEC production decisions"],
                }
            },
            "output_dependencies": {
                "Diesel": {
                    "consumer_sectors": ["Transport"],
                    "competing_products": ["EV Mobility"],
                    "influenced_by": ["GDP Growth"],
                }
            },
        }


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

    llm = StubLLM()
    provider = LLMDrivenEconomicProvider(llm=llm, start="2023-01-01", end="2024-04-01")

    monkeypatch.setattr(provider, "_company_basics", lambda _s: {"company_name": "Oil Company A", "sector": "Energy"})
    monkeypatch.setattr(
        provider,
        "_download_close_series",
        lambda name: {
            "OILCO": _series(1),
            "Oil Company A": _series(1),
            "Brent crude": _series(3),
            "USD/INR": _series(4),
            "OPEC production decisions": _series(6),
            "Diesel": _series(7),
            "GDP Growth": _series(8),
            "Refining Margin": _series(9),
            "OILCO_B": _series(2),
        }.get(name),
    )

    nodes, edges = run_ecosystem(
        "OILCO",
        start="2023-01-01",
        end="2024-04-01",
        data_provider=provider,
        llm=llm,
        validator=StatisticalValidator(corr_threshold=0.05),
        controller=ExpansionController(max_nodes=200, max_depth=3, competitor_limit=3),
    )

    node_names = {n.name for n in nodes}
    assert "Brent crude" in node_names
    assert "USD/INR" in node_names
    assert "Diesel" in node_names
    assert "OILCO_B" in node_names
    assert len(edges) > 0
