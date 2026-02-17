import json
import hashlib
from pathlib import Path


def make_request_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def find_existing_record(path: Path, request_hash: str):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record.get("request_hash") == request_hash:
                return record

    return None