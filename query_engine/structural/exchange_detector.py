EXCHANGE_MAP = {
    "nse": "India NSE",
    "nasdaq": "US NASDAQ",
    "lse": "London Stock Exchange",
}


def detect_exchange(text):
    lower = text.lower()
    for k, v in EXCHANGE_MAP.items():
        if k in lower:
            return v
    return None