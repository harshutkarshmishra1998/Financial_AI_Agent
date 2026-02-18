from typing import Dict

from data_acquisition.common.asset_resolver import AssetResolver
from data_acquisition.common.time_horizon_resolver import TimeHorizonResolver
from data_acquisition.common.ambiguity_handler import AmbiguityHandler
from data_acquisition.common.event_alignment import EventAlignment
from data_acquisition.common.expansion_strategy import ExpansionStrategy

from .planning_models import AcquisitionPlan
from .planning_rules import INTENT_MIN_ROWS, INTENT_DOMAINS


class AcquisitionPlanner:

    def __init__(self):
        self.asset_resolver = AssetResolver()
        self.horizon_resolver = TimeHorizonResolver()
        self.ambiguity_handler = AmbiguityHandler()
        self.event_alignment = EventAlignment()
        self.expansion_strategy = ExpansionStrategy()

    def build_plan(self, query: Dict) -> AcquisitionPlan:

        # assets
        assets = self.asset_resolver.resolve(query)
        assets = self.ambiguity_handler.handle(query, assets)
        assets = self.expansion_strategy.expand(assets, query)

        # time profile
        time_profile = self.horizon_resolver.resolve(query)

        # event window
        event_window = self.event_alignment.align(query)

        # intent
        intent = query.get("intent", "default")

        # min rows
        min_rows = INTENT_MIN_ROWS.get(intent, INTENT_MIN_ROWS["default"])

        # domains
        domains = INTENT_DOMAINS.get(intent, INTENT_DOMAINS["default"])

        # expansion level
        expansion = query.get("retrieval_plan_guidance.search_expansion_level", 1)

        # retry policy
        retry_policy = {
            "max_attempts": 3,
            "progressive_widening": True
        }

        return AcquisitionPlan(
            assets=assets,
            domains=domains,
            time_profile=time_profile,
            min_required_rows=min_rows,
            event_window=event_window,
            expansion_level=expansion,
            retry_policy=retry_policy
        )