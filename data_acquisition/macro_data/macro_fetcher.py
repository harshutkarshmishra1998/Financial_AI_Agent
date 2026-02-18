from typing import Dict

from data_acquisition.macro_data.sources.fred_source import fetch_fred_series
from data_acquisition.macro_data.selectors.macro_selector import MacroSelector


class MacroDataFetcher:

    def __init__(self):
        self.selector = MacroSelector()

    def fetch(self, assets, plan) -> Dict:

        series_map = self.selector.select_series(plan)

        start = None
        end = None

        if plan.event_window:
            start = plan.event_window.get("start")
            end = plan.event_window.get("end")

        results = {}

        for name, series_id in series_map.items():

            observations = fetch_fred_series(series_id, start, end)

            normalized = []

            for o in observations:
                value = o.get("value")
                if value == ".":
                    continue

                normalized.append({
                    "timestamp": o.get("date"),
                    "indicator": name,
                    "value": float(value)
                })

            if normalized:
                results[name] = normalized

        return results