EXCHANGE_KEYWORDS = {
    "nse": "NSE",
    "bse": "BSE",
    "nasdaq": "NASDAQ",
    "nyse": "NYSE",
    "lse": "LSE",
    "tokyo": "TSE",
    "japan": "TSE"
}


def detect_exchange(text: str):
    text = text.lower()
    for key, value in EXCHANGE_KEYWORDS.items():
        if key in text:
            return value
    return None