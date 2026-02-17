import spacy #type: ignore
from .config import SPACY_MODEL

nlp = spacy.load(SPACY_MODEL)


MARKET_TERMS = {
    "market",
    "markets",
    "economy",
    "volatility",
    "rally",
    "selloff",
    "crash",
    "correction",
    "inflation",
    "interest rates"
}

COMMODITY_TERMS = {
    "gold",
    "silver",
    "oil",
    "crude",
    "copper",
    "gas",
    "commodity",
    "metals"
}

NON_FINANCIAL_CONTEXT = {
    "rainforest",
    "fruit",
    "jewelry",
    "weather",
    "climate",
    "farming",
    "agriculture",
    "wildlife"
}

COMPARISON_TERMS = {
    "vs",
    "versus",
    "compare",
    "comparison",
    "correlation"
}


def classify_query_semantics(text: str) -> str:
    text_lower = text.lower()
    doc = nlp(text)

    # -----------------------------------
    # non-financial topic detection
    # -----------------------------------
    if any(term in text_lower for term in NON_FINANCIAL_CONTEXT):
        return "non_financial_topic"

    # -----------------------------------
    # multi asset detection
    # -----------------------------------
    if any(term in text_lower for term in COMPARISON_TERMS):
        return "multi_asset"

    entity_count = sum(1 for ent in doc.ents if ent.label_ in {"ORG", "PRODUCT"})
    if entity_count >= 2:
        return "multi_asset"

    # -----------------------------------
    # commodity topic
    # -----------------------------------
    if any(term in text_lower for term in COMMODITY_TERMS):
        return "commodity_topic"

    # -----------------------------------
    # market-level
    # -----------------------------------
    if any(term in text_lower for term in MARKET_TERMS):
        return "market_level"

    # -----------------------------------
    # asset-specific (default if entity exists)
    # -----------------------------------
    if entity_count >= 1:
        return "asset_specific"

    # fallback
    return "unknown"