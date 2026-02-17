import json
from pathlib import Path


def write_jsonl(path, rows):
    path.parent.mkdir(exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, default=lambda o: o.__dict__) + "\n")