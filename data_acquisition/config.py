from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

QUERY_LOG_PATH = DATA_DIR / "query_logs.jsonl"
MARKET_DATA_PATH = DATA_DIR / "market_data.jsonl"
MACRO_DATA_PATH = DATA_DIR / "macro_data.jsonl"
NEWS_DATA_PATH = DATA_DIR / "news_data.jsonl"
FLOW_DATA_PATH = DATA_DIR / "flow_data.jsonl"


# -----------------------------
# TIME HORIZON DEFAULT MAPPING
# Editable anytime
# -----------------------------

TIME_HORIZON_TO_DAYS = {
    "intraday": 1,
    "short_term": 30,
    "medium_term": 180,
    "long_term": 1825
}


# -----------------------------
# ASSET SELECTION STRATEGY
# -----------------------------
USE_PRIMARY_ASSET_ONLY = True