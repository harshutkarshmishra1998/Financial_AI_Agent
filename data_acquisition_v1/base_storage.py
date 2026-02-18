import json
from datetime import datetime
from pathlib import Path


def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)

    record["created_at"] = datetime.utcnow().isoformat()

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")