from ..base_storage import append_jsonl
from ..config import FLOW_DATA_PATH


def append_flow_record(record: dict):
    append_jsonl(FLOW_DATA_PATH, record)