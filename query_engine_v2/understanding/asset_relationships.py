import spacy #type: ignore
from .config import SPACY_MODEL

nlp = spacy.load(SPACY_MODEL)


COMPARISON_TERMS = {
    "compare", "vs", "versus", "outperform", "underperform",
    "better than", "worse than"
}

CORRELATION_TERMS = {
    "correlation", "correlate", "relationship between",
    "move together", "linked with"
}

CAUSAL_TERMS = {
    "because", "due to", "caused by", "impact of",
    "effect of", "driven by", "influenced by",
    "led to", "result of"
}

HEDGE_TERMS = {
    "hedge", "protect against", "offset risk",
    "safe haven", "diversify"
}

SPREAD_TERMS = {
    "spread", "price difference", "arbitrage",
    "pair trade", "relative value"
}

PORTFOLIO_TERMS = {
    "portfolio", "allocation", "weighting",
    "diversification", "basket"
}


def detect_direction(text: str):
    """
    Detect directional language like:
    'Bitcoin rise causing gold fall'
    """
    text = text.lower()

    if any(w in text for w in ["rise", "increase", "up"]):
        return "positive_movement"

    if any(w in text for w in ["fall", "drop", "decline", "down"]):
        return "negative_movement"

    return None


def classify_asset_relationship(text: str, asset_count: int):
    """
    Determine how assets relate to each other.
    """

    if asset_count <= 1:
        return {
            "relationship_type": "single_asset",
            "direction": None,
            "confidence": 1.0
        }

    text_lower = text.lower()

    # explicit relationship keywords
    if any(t in text_lower for t in CAUSAL_TERMS):
        return {
            "relationship_type": "causal",
            "direction": detect_direction(text),
            "confidence": 0.9
        }

    if any(t in text_lower for t in CORRELATION_TERMS):
        return {
            "relationship_type": "correlation",
            "direction": None,
            "confidence": 0.9
        }

    if any(t in text_lower for t in HEDGE_TERMS):
        return {
            "relationship_type": "hedge",
            "direction": None,
            "confidence": 0.85
        }

    if any(t in text_lower for t in SPREAD_TERMS):
        return {
            "relationship_type": "spread",
            "direction": None,
            "confidence": 0.85
        }

    if any(t in text_lower for t in PORTFOLIO_TERMS):
        return {
            "relationship_type": "portfolio",
            "direction": None,
            "confidence": 0.85
        }

    if any(t in text_lower for t in COMPARISON_TERMS):
        return {
            "relationship_type": "comparison",
            "direction": None,
            "confidence": 0.8
        }

    # syntactic comparison detection (Tesla and Nvidia performance)
    doc = nlp(text)
    conjunctions = [token for token in doc if token.dep_ == "cc"]

    if conjunctions:
        return {
            "relationship_type": "comparison",
            "direction": None,
            "confidence": 0.6
        }

    return {
        "relationship_type": "unknown_multi",
        "direction": None,
        "confidence": 0.4
    }