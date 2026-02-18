import yaml
from pathlib import Path
from typing import Dict, Any


CONFIG_DIR = Path("data_acquisition/config")


class TimeHorizonResolver:

    def __init__(self):
        with open(CONFIG_DIR / "time_horizon_config.yaml") as f:
            self.horizon_config = yaml.safe_load(f)

        with open(CONFIG_DIR / "fetch_profiles.yaml") as f:
            self.fetch_profiles = yaml.safe_load(f)

        with open(CONFIG_DIR / "acquisition_defaults.yaml") as f:
            self.defaults = yaml.safe_load(f)

    def resolve(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns fetch profile.
        """

        # 1 explicit time range from interpretation
        if query.get("time_range.type") == "rolling_window":
            return {
                "start": query.get("time_range.start"),
                "end": query.get("time_range.end"),
                "mode": "explicit_range"
            }

        # 2 keyword-based mapping
        text = query.get("user_query", "").lower()

        for horizon, keywords in self.horizon_config["keyword_mapping"].items(): #type: ignore
            if any(k in text for k in keywords):
                return self.fetch_profiles[horizon] #type: ignore

        # 3 semantic horizon
        for name, info in self.horizon_config.get("semantic_horizons", {}).items(): #type: ignore
            if name in text:
                return info

        # 4 default
        return self.fetch_profiles[self.defaults["default_time_horizon"]] #type: ignore