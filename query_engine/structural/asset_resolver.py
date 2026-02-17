from query_engine.schema.asset_model import Asset

ASSET_DB = {
    "tesla": ("TSLA", "equity", "US"),
    "bitcoin": ("BTC", "crypto", None),
    "gold": ("XAU", "commodity", None),
    "reliance": ("RELIANCE.NS", "equity", "India"),
}


def resolve_assets(text: str):
    assets = []
    lower = text.lower()

    for name, (ticker, cls, country) in ASSET_DB.items():
        if name in lower:
            assets.append(
                Asset(
                    name=name,
                    ticker=ticker,
                    asset_class=cls,
                    country=country,
                    resolved=True,
                    confidence=0.9
                )
            )
    return assets