# import json
# from .config import QUERY_LOG_PATH


# def load_last_queries(n: int):
#     if not QUERY_LOG_PATH.exists():
#         return []

#     with open(QUERY_LOG_PATH, "r", encoding="utf-8") as f:
#         lines = f.readlines()

#     selected = lines[-n:] if n else lines

#     return [json.loads(line) for line in selected]

import json
from .config import QUERY_LOG_PATH


def load_last_queries(n: int):

    if not QUERY_LOG_PATH.exists():
        return []

    valid = []

    with open(QUERY_LOG_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                valid.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"[WARNING] Skipping corrupted JSONL line {i}")

    if n:
        return valid[-n:]

    return valid