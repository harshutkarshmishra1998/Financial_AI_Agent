from pathlib import Path

# spaCy
SPACY_MODEL = "en_core_web_sm"

# Storage
DATA_DIR = Path("data")
QUERY_LOG_FILE = DATA_DIR / "query_logs.jsonl"

# Intent labels (deterministic)
INTENT_LABELS = {
    "price_movement": ["why", "rise", "fall", "increase", "decrease", "drop", "gain"],
    "volatility": ["volatility", "fluctuation", "unstable"],
    "market_outlook": ["outlook", "future", "next", "expect", "forecast"],
    "general_info": []
}

# Forecast trigger keywords
FORECAST_KEYWORDS = [
    "forecast",
    "predict",
    "prediction",
    "future",
    "expected",
    "outlook",
    "will",
    "next"
]

# Time horizon categories
TIME_BUCKETS = {
    "intraday": ["today", "now", "hour"],
    "short_term": ["week", "days"],
    "medium_term": ["month", "quarter"],
    "long_term": ["year", "years"]
}