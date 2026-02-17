import jsonlines #type: ignore
from pathlib import Path
from .config import QUERY_LOG_FILE, DATA_DIR


def append_query_log(record: dict):
    # ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ensure file exists
    if not QUERY_LOG_FILE.exists():
        QUERY_LOG_FILE.touch()

    with jsonlines.open(QUERY_LOG_FILE, mode="a") as writer:
        writer.write(record)