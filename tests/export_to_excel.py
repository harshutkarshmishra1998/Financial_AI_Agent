from pathlib import Path
import json
import pandas as pd


# -------------------------------------------------
# CONFIG
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "query_logs_cleaned.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "data" / "query_logs_cleaned.xlsx"


# -------------------------------------------------
# LOAD JSONL
# -------------------------------------------------
def load_jsonl(path: Path):
    records = []

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


# -------------------------------------------------
# EXPORT
# -------------------------------------------------
def export_to_excel():

    print("Loading JSONL...")
    data = load_jsonl(INPUT_FILE)

    if not data:
        print("No records found.")
        return

    print("Flattening records...")
    df = pd.json_normalize(data)

    print("Writing Excel...")
    df.to_excel(OUTPUT_FILE, index=False)

    print("Done.")
    print("Saved to:", OUTPUT_FILE)


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    export_to_excel()