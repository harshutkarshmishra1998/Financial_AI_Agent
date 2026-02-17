import math


def normalize_score(raw_score: float) -> float:
    """Convert arbitrary score into 0–1 probability-like scale."""
    return 1 / (1 + math.exp(-raw_score))


def compute_confidence(top_score: float, second_score: float | None):
    """
    Confidence depends on:
    1. absolute score strength
    2. separation from next candidate
    """
    base = normalize_score(top_score)

    if second_score is None:
        return round(base, 3)

    separation = top_score - second_score

    # confidence increases if clear winner
    separation_bonus = normalize_score(separation) * 0.5

    return round(min(base + separation_bonus, 1.0), 3)


def is_ambiguous(confidence: float, threshold: float = 0.6):
    return confidence < threshold