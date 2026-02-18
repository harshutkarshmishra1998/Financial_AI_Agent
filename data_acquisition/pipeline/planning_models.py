from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class AcquisitionPlan:
    assets: List[str]
    domains: List[str]
    time_profile: Dict
    min_required_rows: int
    event_window: Optional[Dict]
    expansion_level: int
    retry_policy: Dict
