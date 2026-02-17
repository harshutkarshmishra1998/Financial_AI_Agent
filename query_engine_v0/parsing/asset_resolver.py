COMPANY_MAP = {
    "tesla": "TSLA",
    "apple": "AAPL",
    "reliance": "RELIANCE.NS",
}


def resolve_assets(record):
    q = record["user_query"].lower()

    for name, ticker in COMPANY_MAP.items():
        if name in q:
            record["primary_asset"] = name
            record["ticker"] = ticker
            break

    return record