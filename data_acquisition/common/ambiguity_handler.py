# import yaml
# from pathlib import Path
# from typing import Dict, Any, List


# CONFIG = Path("data_acquisition/config/acquisition_defaults.yaml")


# class AmbiguityHandler:

#     def __init__(self):
#         with open(CONFIG) as f:
#             self.defaults = yaml.safe_load(f)

#     def handle(self, query: Dict[str, Any], resolved_assets: List[str]) -> List[str]:
#         """
#         If ambiguity high → use macro basket.
#         """

#         score = query.get("interpretation_validation.completeness_score", 1.0)

#         if score < self.defaults["ambiguity_threshold"]: #type: ignore
#             return self.defaults["default_macro_basket"] #type: ignore

#         return resolved_assets

import yaml
from pathlib import Path
from typing import Dict, Any, List


CONFIG = Path("data_acquisition/config/acquisition_defaults.yaml")


class AmbiguityHandler:

    def __init__(self):
        with open(CONFIG) as f:
            self.defaults = yaml.safe_load(f)

    def handle(self, query: Dict[str, Any], resolved_assets: List[str]) -> List[str]:
        """
        Ambiguity handling policy:

        - If ambiguity high AND no primary assets → macro basket
        - If ambiguity high AND primary assets exist → expand with macro context
        """

        score = query.get("interpretation_validation.completeness_score", 1.0)

        if score < self.defaults["ambiguity_threshold"]:

            macro = self.defaults["default_macro_basket"]

            if not resolved_assets:
                return macro

            # preserve primary + add context
            return list(set(resolved_assets + macro))

        return resolved_assets