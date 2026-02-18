# import pandas as pd
# from typing import Dict


# class DataQualityEvaluator:
#     """
#     Computes quality metrics for datasets.
#     Used for fallback and source selection.
#     """

#     @staticmethod
#     def evaluate_market(df: pd.DataFrame) -> Dict:
#         if df is None or df.empty:
#             return {
#                 "valid": False,
#                 "rows": 0,
#                 "completeness": 0.0,
#                 "sparsity": 1.0
#             }

#         total_cells = df.size
#         missing = df.isna().sum().sum()

#         completeness = 1 - (missing / total_cells) if total_cells else 0

#         numeric = df.select_dtypes(include=["float", "int"])
#         sparsity = numeric.isna().mean().mean() if not numeric.empty else 1

#         valid = (
#             len(df) >= 5 and
#             completeness > 0.7 and
#             sparsity < 0.5 and
#             {"open", "high", "low", "close"}.issubset(df.columns)
#         )

#         return {
#             "valid": valid,
#             "rows": len(df),
#             "completeness": round(completeness, 3),
#             "sparsity": round(sparsity, 3)
#         }

import pandas as pd
from typing import Dict, Optional


class DataQualityEvaluator:
    """
    Computes quality metrics for datasets.
    Validity depends on minimum required rows.
    """

    DEFAULT_MIN_ROWS = 5

    @staticmethod
    def evaluate_market(
        df: pd.DataFrame,
        min_rows: Optional[int] = None
    ) -> Dict:

        if min_rows is None:
            min_rows = DataQualityEvaluator.DEFAULT_MIN_ROWS

        if df is None or df.empty:
            return {
                "valid": False,
                "rows": 0,
                "completeness": 0.0,
                "sparsity": 1.0
            }

        total_cells = df.size
        missing = df.isna().sum().sum()

        completeness = 1 - (missing / total_cells) if total_cells else 0

        numeric = df.select_dtypes(include=["float", "int"])
        sparsity = numeric.isna().mean().mean() if not numeric.empty else 1

        valid = (
            len(df) >= min_rows and
            completeness > 0.7 and
            sparsity < 0.5 and
            {"open", "high", "low", "close"}.issubset(df.columns)
        )

        return {
            "valid": valid,
            "rows": len(df),
            "completeness": round(completeness, 3),
            "sparsity": round(sparsity, 3)
        }