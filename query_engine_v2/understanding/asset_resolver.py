import spacy
import yfinance as yf
from functools import lru_cache

from .config import SPACY_MODEL
from .asset_llm_fallback import normalize_asset_name
from .asset_models import ResolvedAsset, AssetResolutionResult
from .asset_scoring import score_asset_match
from .market_index_resolver import resolve_index
from .exchange_detector import detect_exchange
from .resolution_confidence import compute_confidence, is_ambiguous


nlp = spacy.load(SPACY_MODEL)


# --------------------------------------------------
# multi asset extraction
# --------------------------------------------------
def extract_asset_candidates(text: str):
    doc = nlp(text)
    candidates = set()

    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT"}:
            candidates.add(ent.text)

    for token in doc:
        if token.text.lower() in {"stock", "price", "shares", "token"}:
            if token.i > 0:
                candidates.add(doc[token.i - 1].text)

    return list(candidates)


# --------------------------------------------------
# asset type inference
# --------------------------------------------------
def infer_asset_type(symbol: str, info: dict):
    qt = info.get("quoteType")

    if qt == "EQUITY":
        return "equity"
    if qt == "CRYPTOCURRENCY":
        return "crypto"
    if qt == "ETF":
        return "etf"
    if qt == "INDEX":
        return "index"
    if symbol.endswith("=F"):
        return "commodity"

    return "unknown"


# --------------------------------------------------
# search + rank all candidates
# --------------------------------------------------
def search_ranked_symbols(candidate: str, query: str, exchange: str | None):
    results = []

    try:
        search = yf.Search(candidate, max_results=10)

        for q in search.quotes:
            symbol = q["symbol"]

            ticker = yf.Ticker(symbol)
            info = ticker.info

            asset_type = infer_asset_type(symbol, info)

            score = score_asset_match(candidate, symbol, asset_type, query)

            results.append(
                ResolvedAsset(
                    name=info.get("longName") or candidate,
                    ticker=symbol,
                    asset_type=asset_type,
                    exchange=exchange,
                    resolved=True,
                    resolution_method="ranked_symbol_search",
                    score=score
                )
            )

    except Exception:
        pass

    results.sort(key=lambda x: x.score, reverse=True)
    return results


# --------------------------------------------------
# resolve single candidate with ranking
# --------------------------------------------------
def resolve_candidate(candidate: str, query: str, exchange: str | None):
    ranked = search_ranked_symbols(candidate, query, exchange)

    if not ranked:
        normalized = normalize_asset_name(candidate)
        if normalized:
            ranked = search_ranked_symbols(normalized, query, exchange)

    return ranked


# --------------------------------------------------
# main resolver
# --------------------------------------------------
@lru_cache(maxsize=512)
def resolve_assets(query: str):

    exchange = detect_exchange(query)

    # index override
    idx = resolve_index(query)
    if idx:
        asset = ResolvedAsset(**idx, score=10.0)
        return AssetResolutionResult(
            assets=[asset],
            primary_asset=asset,
            confidence=1.0,
            ambiguous=False
        )

    candidates = extract_asset_candidates(query)

    all_ranked = []

    for c in candidates:
        ranked = resolve_candidate(c, query, exchange)
        all_ranked.extend(ranked)

    if not all_ranked:
        return AssetResolutionResult(
            assets=[],
            primary_asset=None,
            confidence=0.0,
            ambiguous=False
        )

    all_ranked.sort(key=lambda x: x.score, reverse=True)

    primary = all_ranked[0]
    second = all_ranked[1] if len(all_ranked) > 1 else None

    confidence = compute_confidence(
        primary.score,
        second.score if second else None
    )

    return AssetResolutionResult(
        assets=all_ranked[:5],  # top 5 candidates retained
        primary_asset=primary,
        confidence=confidence,
        ambiguous=is_ambiguous(confidence)
    )