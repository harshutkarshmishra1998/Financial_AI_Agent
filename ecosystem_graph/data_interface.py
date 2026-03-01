from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import pandas as pd
import yfinance as yf

from .llm_interface import GroqLLM


class TimeSeriesProvider:
    """
    Interface-first provider.
    Production implementations can back these methods with APIs/DB/knowledge graphs.
    Tests can pass in-memory dictionaries.
    """

    def __init__(
        self,
        company_map: Optional[Dict[str, Dict]] = None,
        series_map: Optional[Dict[str, pd.Series]] = None,
    ):
        self.company_map = company_map or {}
        self.series_map = series_map or {}

    def get_company_profile(self, symbol: str) -> Dict:
        return self.company_map.get(symbol, {})

    def get_series(self, entity_name: str) -> Optional[pd.Series]:
        series = self.series_map.get(entity_name)
        if series is None:
            return None
        s = pd.Series(series).dropna()
        if not isinstance(s.index, pd.DatetimeIndex):
            s.index = pd.to_datetime(s.index)
        return s.sort_index()

    def get_input_dependencies(self, symbol: str, input_name: str) -> Dict[str, List[str]]:
        profile = self.get_company_profile(symbol)
        return profile.get("input_dependencies", {}).get(input_name, {})

    def get_output_dependencies(self, symbol: str, output_name: str) -> Dict[str, List[str]]:
        profile = self.get_company_profile(symbol)
        return profile.get("output_dependencies", {}).get(output_name, {})

    def iter_company_inputs(self, symbol: str) -> Iterable[Dict]:
        return self.get_company_profile(symbol).get("inputs", [])

    def iter_company_outputs(self, symbol: str) -> Iterable[Dict]:
        return self.get_company_profile(symbol).get("outputs", [])

    def iter_competitors(self, symbol: str) -> List[str]:
        return self.get_company_profile(symbol).get("competitors", [])


class LLMDrivenEconomicProvider(TimeSeriesProvider):
    """
    Auto-build provider from symbol without hardcoded sector/company rules.
    - Fetches company metadata and market series from yfinance.
    - Uses LLM to infer ecosystem dependencies.
    - Falls back to minimal profile if LLM unavailable.
    """

    def __init__(self, llm: Optional[GroqLLM] = None, start: Optional[str] = None, end: Optional[str] = None):
        super().__init__(company_map={}, series_map={})
        self.llm = llm or GroqLLM()
        self.start = start
        self.end = end

    def _download_close_series(self, query: str) -> Optional[pd.Series]:
        try:
            df = yf.download(query, start=self.start, end=self.end, period=None if self.start else "5y", progress=False)
            if df.empty:  # type: ignore
                return None
            if isinstance(df.columns, pd.MultiIndex):  # type: ignore
                df.columns = df.columns.get_level_values(0)  # type: ignore
            if "Close" in df.columns:  # type: ignore
                s = pd.Series(df["Close"]).dropna()  # type: ignore
            else:
                return None
            s.index = pd.to_datetime(s.index)
            return s.sort_index()
        except Exception:
            return None

    def _company_basics(self, symbol: str) -> Dict[str, str]:
        try:
            info = yf.Ticker(symbol).info
        except Exception:
            info = {}

        company_name = info.get("longName") or info.get("shortName") or symbol
        sector = info.get("sector") or "Unknown"
        return {"company_name": company_name, "sector": sector}

    def get_company_profile(self, symbol: str) -> Dict:
        if symbol in self.company_map:
            return self.company_map[symbol]

        basics = self._company_basics(symbol)
        profile = {
            "company_name": basics["company_name"],
            "sector": basics["sector"],
            "inputs": [],
            "outputs": [],
            "competitors": [],
            "input_dependencies": {},
            "output_dependencies": {},
        }

        llm_profile = self.llm.extract_company_profile(symbol, basics["company_name"], basics["sector"])
        if isinstance(llm_profile, dict):
            profile.update(llm_profile)

        self.company_map[symbol] = profile

        company_series = self._download_close_series(symbol)
        if company_series is not None:
            self.series_map[profile["company_name"]] = company_series

        # Preload obvious entity series candidates to improve hybrid validation hit-rate.
        entity_names: List[str] = []
        entity_names.extend([i.get("name", "") for i in profile.get("inputs", [])])
        entity_names.extend([o.get("name", "") for o in profile.get("outputs", [])])
        entity_names.extend(profile.get("competitors", []))
        for dep in profile.get("input_dependencies", {}).values():
            entity_names.extend(dep.get("producers", []))
            entity_names.extend(dep.get("competing_materials", []))
            entity_names.extend(dep.get("influenced_by", []))
        for dep in profile.get("output_dependencies", {}).values():
            entity_names.extend(dep.get("consumer_sectors", []))
            entity_names.extend(dep.get("competing_products", []))
            entity_names.extend(dep.get("influenced_by", []))

        for name in {n for n in entity_names if n}:
            if name in self.series_map:
                continue
            s = self._download_close_series(name)
            if s is not None:
                self.series_map[name] = s

        return profile
