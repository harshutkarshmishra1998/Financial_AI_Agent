INDEX_MAP = {
    "s&p 500": "^GSPC",
    "sp500": "^GSPC",
    "dow jones": "^DJI",
    "nasdaq": "^IXIC",
    "nifty 50": "^NSEI",
    "sensex": "^BSESN",
    "ftse 100": "^FTSE"
}


def resolve_index(text: str):
    text_lower = text.lower()

    for name, symbol in INDEX_MAP.items():
        if name in text_lower:
            return {
                "name": name.upper(),
                "ticker": symbol,
                "asset_type": "index",
                "exchange": None,
                "resolved": True,
                "resolution_method": "index_map"
            }

    return None