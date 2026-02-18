from typing import Dict


class SourceScorer:
    """
    Converts quality metrics into comparable score.
    """

    WEIGHTS = {
        "rows": 0.3,
        "completeness": 0.5,
        "sparsity": -0.2
    }

    @staticmethod
    def score(quality: Dict) -> float:

        if not quality.get("valid"):
            return 0.0

        rows_score = min(quality["rows"] / 100, 1)
        completeness_score = quality["completeness"]
        sparsity_penalty = quality["sparsity"]

        score = (
            rows_score * SourceScorer.WEIGHTS["rows"]
            + completeness_score * SourceScorer.WEIGHTS["completeness"]
            + sparsity_penalty * SourceScorer.WEIGHTS["sparsity"]
        )

        return round(score, 4)