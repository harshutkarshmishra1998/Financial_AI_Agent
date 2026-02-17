import json
from pathlib import Path
from typing import Any, Dict, List, TypedDict


# -------------------------------------------------
# PATH CONFIG
# -------------------------------------------------

DATA_DIR = Path("data")

INPUT_PATH = DATA_DIR / "query_logs_final.jsonl"
OUTPUT_PATH = DATA_DIR / "query_logs_cleaned.jsonl"

FILES_TO_DELETE = [
    DATA_DIR / "query_logs_enriched.jsonl",
    DATA_DIR / "clarification_audit.jsonl",
    DATA_DIR / "clarification_answers.jsonl",
    DATA_DIR /"query_logs_final.jsonl",
]


# -------------------------------------------------
# RESULT TYPE
# -------------------------------------------------

class CleaningResult(TypedDict):
    processed: int
    deleted_files: List[str]


# -------------------------------------------------
# GENERIC HELPERS
# -------------------------------------------------

def _is_empty(v: Any) -> bool:
    return v in (None, "", [], {}, "unknown")


def _flatten(d: Dict[str, Any], parent: str = "", sep: str = ".") -> Dict[str, Any]:
    items: List[tuple[str, Any]] = []

    for k, v in d.items():
        new_key = f"{parent}{sep}{k}" if parent else k

        if isinstance(v, dict):
            items.extend(_flatten(v, new_key, sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def _extract_meta(d: Dict[str, Any]) -> Dict[str, Any]:
    clean: Dict[str, Any] = {}

    for k, v in d.items():
        if isinstance(v, dict) and "value" in v:
            clean[k] = v["value"]
        else:
            clean[k] = v

    return clean


def _normalize_assets(assets: Any) -> List[Dict[str, Any]]:
    if not assets:
        return []

    if not isinstance(assets, list):
        assets = [assets]

    normalized: List[Dict[str, Any]] = []
    seen = set()

    for a in assets:
        if isinstance(a, dict):
            item = {
                "name": a.get("name"),
                "ticker": a.get("ticker"),
                "type": a.get("asset_type"),
                "score": a.get("score"),
            }
        else:
            item = {"name": a}

        key = item.get("ticker") or item.get("name")

        if key and key not in seen:
            seen.add(key)
            normalized.append(item)

    return normalized


def _remove_empty(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if not _is_empty(v)}


# -------------------------------------------------
# RECORD CLEANING
# -------------------------------------------------

def clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(record)

    if isinstance(r.get("enrichment_meta"), dict):
        r.update(_extract_meta(r["enrichment_meta"]))
        del r["enrichment_meta"]

    r["assets"] = _normalize_assets(r.get("assets"))

    if r.get("primary_asset"):
        pa = _normalize_assets([r["primary_asset"]])
        r["primary_asset"] = pa[0] if pa else None

    r = _flatten(r)
    r = _remove_empty(r)

    return r


# -------------------------------------------------
# FILE OPERATIONS
# -------------------------------------------------

def _read_last_n(path: Path, n: int) -> List[Dict[str, Any]]:
    if not path.exists() or n <= 0:
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return [json.loads(line) for line in lines[-n:]]


def _append_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    if not records:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _delete_intermediate_files() -> List[str]:
    deleted: List[str] = []

    for file_path in FILES_TO_DELETE:
        try:
            if file_path.exists():
                file_path.unlink()
                deleted.append(file_path.name)
        except Exception:
            # never break pipeline due to cleanup failure
            pass

    return deleted


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def clean_last_n_entries(last_n: int) -> CleaningResult:
    """
    Clean last N entries from raw logs,
    append to cleaned log,
    remove intermediate logs.

    Returns structured result for pipeline state.
    """

    raw_records = _read_last_n(INPUT_PATH, last_n)
    cleaned = [clean_record(r) for r in raw_records]

    _append_jsonl(OUTPUT_PATH, cleaned)
    deleted_files = _delete_intermediate_files()

    return CleaningResult(
        processed=len(cleaned),
        deleted_files=deleted_files,
    )