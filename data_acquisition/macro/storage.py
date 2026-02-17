from ..base_storage import append_jsonl
from ..config import MACRO_DATA_PATH


def append_macro_record(record: dict):
    append_jsonl(MACRO_DATA_PATH, record)