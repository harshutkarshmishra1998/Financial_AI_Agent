from .config import INTENT_LABELS, FORECAST_KEYWORDS


def classify_intent(text: str):
    text_lower = text.lower()

    if any(k in text_lower for k in FORECAST_KEYWORDS):
        return "forecast_request"

    for label, keywords in INTENT_LABELS.items():
        if any(k in text_lower for k in keywords):
            return label

    return "general_info"