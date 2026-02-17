INDEX_MAP = {
    "s&p 500": "SPX",
    "nifty": "NIFTY50",
    "dow": "DJI"
}


def detect_index(text):
    lower = text.lower()
    for k, v in INDEX_MAP.items():
        if k in lower:
            return v
    return None