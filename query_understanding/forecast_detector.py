from .config import FORECAST_KEYWORDS


def detect_forecast_request(text: str) -> bool:
    text_lower = text.lower()
    return any(k in text_lower for k in FORECAST_KEYWORDS)