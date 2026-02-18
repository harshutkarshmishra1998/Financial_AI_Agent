import json
from pathlib import Path
from datetime import datetime


# -------------------------------------------------
# PATH CONFIG
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True)

MARKET_FILE = DATA_DIR / "market.jsonl"
NEWS_FILE = DATA_DIR / "news.jsonl"
MACRO_FILE = DATA_DIR / "macro.jsonl"


# -------------------------------------------------
# UTIL
# -------------------------------------------------
def _utc_now():
    return datetime.utcnow().isoformat() + "Z"

import pandas as pd
import numpy as np


def _json_safe(obj):
    """
    Recursively convert objects into JSON serializable form.
    """

    # pandas timestamp
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()

    # numpy types
    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        return float(obj)

    # numpy arrays
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # dict
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}

    # list
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]

    return obj


def _append_jsonl(path: Path, record: dict):
    with open(path, "a", encoding="utf-8") as f:
        # f.write(json.dumps(record, ensure_ascii=False) + "\n")
        safe_record = _json_safe(record)
        f.write(json.dumps(safe_record, ensure_ascii=False) + "\n")


# -------------------------------------------------
# MARKET SNAPSHOT
# -------------------------------------------------
def write_market_snapshot(query_id: str, market_data: dict):

    if not market_data:
        return

    for asset, info in market_data.items():

        df = info["data"]

        record = {
            "query_id": query_id,
            "asset": asset,
            "source": info["source"],
            "rows": info["rows"],
            "attempts": info["attempts"],
            "fetched_at": _utc_now(),
            "data": df.to_dict(orient="records")
        }

        _append_jsonl(MARKET_FILE, record)


# -------------------------------------------------
# NEWS SNAPSHOT
# -------------------------------------------------
def write_news_snapshot(query_id: str, news_data: dict):

    if not news_data:
        return

    for asset, articles in news_data.items():

        record = {
            "query_id": query_id,
            "asset": asset,
            "num_articles": len(articles),
            "fetched_at": _utc_now(),
            "articles": articles
        }

        _append_jsonl(NEWS_FILE, record)





def write_macro_snapshot(query_id: str, macro_data: dict):

    if not macro_data:
        return

    for indicator, values in macro_data.items():

        record = {
            "query_id": query_id,
            "indicator": indicator,
            "num_points": len(values),
            "fetched_at": _utc_now(),
            "data": values
        }

        _append_jsonl(MACRO_FILE, record)
