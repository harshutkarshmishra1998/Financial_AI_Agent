from ..base_storage import append_jsonl
from ..config import NEWS_DATA_PATH


def append_news_record(record: dict):
    append_jsonl(NEWS_DATA_PATH, record)