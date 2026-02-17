import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta


# =========================================================
# FILE PATHS
# =========================================================

ENRICHED = Path("data/query_logs_enriched.jsonl")
CLARIFICATION_AUDIT = Path("data/clarification_audit.jsonl")

GENERATED_ANSWERS = Path("data/clarification_answers.jsonl")
FINAL_LOGS = Path("data/query_logs_final.jsonl")


# =========================================================
# IO HELPERS
# =========================================================

def load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def write_jsonl(path: Path, rows: List[Dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# =========================================================
# AUTO ANSWER GENERATION (TEMPORARY SIMULATION)
# =========================================================

def default_recent_window(days=14):
    today = datetime.utcnow().date()
    return {
        "type": "rolling_window",
        "start": str(today - timedelta(days=days)),
        "end": str(today),
        "source": "auto_default"
    }


def generate_auto_answers(audit_records: List[Dict]) -> List[Dict]:
    """
    Generate answers for ALL clarification questions.
    This simulates user input for now.
    """

    answers = []

    for row in audit_records:

        if not row["clarification_required"]:
            continue

        qid = row["query_id"]
        missing = row["missing_dimensions"]

        ans = {}

        # ------------------------------
        # time
        # ------------------------------
        if "time_range" in missing:
            ans["time_range"] = default_recent_window()

        # ------------------------------
        # direction
        # ------------------------------
        if "movement_direction" in missing:
            ans["movement_direction"] = "down"  # neutral default

        # ------------------------------
        # event
        # ------------------------------
        if "event_context" in missing:
            ans["event_context"] = {
                "event_type": "unspecified_event",
                "temporal_relation": "unknown",
                "source": "auto_default"
            }

        # ------------------------------
        # entity scope
        # ------------------------------
        if "asset_scope" in missing or "entity_scope_level" in missing:
            ans["entity_scope_level"] = "single_asset"

        # ------------------------------
        # intent
        # ------------------------------
        if "intent" in missing:
            ans["intent"] = "causal_explanation"

        # ------------------------------
        # comparison
        # ------------------------------
        if "comparison_target" in missing:
            ans["comparison_target"] = "previous_period"

        answers.append({
            "query_id": qid,
            "answers": ans
        })

    return answers


# =========================================================
# APPLY ANSWERS TO RECORDS
# =========================================================

def apply_answers(enriched: List[Dict], answers: List[Dict]) -> List[Dict]:

    answer_map = {a["query_id"]: a["answers"] for a in answers}

    updated = []

    for r in enriched:

        qid = r["query_id"]

        if qid not in answer_map:
            updated.append(r)
            continue

        ans = answer_map[qid]

        # apply updates directly
        for k, v in ans.items():
            r[k] = v

        # mark resolution
        r["clarification_resolved"] = True

        updated.append(r)

    return updated


# =========================================================
# MAIN PROCESSOR
# =========================================================

def run_clarification_processor():

    print("Loading enriched interpretation...")
    enriched = load_jsonl(ENRICHED)

    print("Loading clarification audit...")
    audit = load_jsonl(CLARIFICATION_AUDIT)

    print("Generating auto clarification answers...")
    answers = generate_auto_answers(audit)
    write_jsonl(GENERATED_ANSWERS, answers)

    print("Applying answers to records...")
    final_records = apply_answers(enriched, answers)

    print("Saving final query logs...")
    write_jsonl(FINAL_LOGS, final_records)

    print("\nDONE")
    print("Generated answers →", GENERATED_ANSWERS)
    print("Final resolved logs →", FINAL_LOGS)


# =========================================================
# ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    run_clarification_processor()