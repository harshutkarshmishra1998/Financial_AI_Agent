from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import pandas as pd


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
        """
        Expected keys (all optional):
        - company_name, sector
        - inputs: [{"name": "..."}]
        - outputs: [{"name": "..."}]
        - competitors: ["..."]
        - input_dependencies: {"Input": {"producers": [], "competing_materials": [], "influenced_by": []}}
        - output_dependencies: {"Output": {"consumer_sectors": [], "competing_products": [], "influenced_by": []}}
        """
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
