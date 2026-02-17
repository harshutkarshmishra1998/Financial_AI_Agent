def score_asset_match(candidate: str, symbol: str, asset_type: str, query: str):
    score = 0.0
    q = query.lower()

    # exact name match bonus
    if candidate.lower() in symbol.lower():
        score += 2.0

    # commodity context
    if asset_type == "commodity" and any(k in q for k in ["price", "commodity", "futures"]):
        score += 2.0

    # crypto context
    if asset_type == "crypto" and any(k in q for k in ["crypto", "token", "coin"]):
        score += 2.0

    # equity context
    if asset_type == "equity" and any(k in q for k in ["stock", "shares", "earnings"]):
        score += 2.0

    return score