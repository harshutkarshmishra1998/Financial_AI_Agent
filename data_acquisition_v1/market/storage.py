from ..base_storage import append_jsonl
from ..config import MARKET_DATA_PATH


def append_market_record(record: dict):
    append_jsonl(MARKET_DATA_PATH, record)