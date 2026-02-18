from typing import List, Dict, Any


class ExpansionStrategy:

    def expand(self, base_assets: List[str], query: Dict[str, Any]) -> List[str]:
        """
        Expands asset set based on search expansion level.
        """

        level = query.get("retrieval_plan_guidance.search_expansion_level", 1)

        if level <= 1:
            return base_assets

        if level == 2:
            return base_assets  # peers can be added later

        if level >= 3:
            # sector / macro broadening handled elsewhere
            return base_assets

        return base_assets