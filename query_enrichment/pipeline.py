import json
from pathlib import Path
from typing import List, Dict

# =========================================================
# CORE ENRICHMENT
# =========================================================

from query_enrichment.enrichment_core import enrich_record


# =========================================================
# SEMANTIC INTERPRETATION
# =========================================================

from query_enrichment.intent_classifier import classify_intent
from query_enrichment.direction_extractor import extract_direction
from query_enrichment.temporal_normalizer import normalize_time_expression

from query_enrichment.entity_hierarchy_resolver import resolve_entity_scope
from query_enrichment.event_semantic_detector import detect_event_context


# =========================================================
# VALIDATION + PLANNING
# =========================================================

from query_enrichment.interpretation_validator import validate_records
from query_enrichment.retrieval_scope_advisor import recommend_scope
from query_enrichment.quality_reporter import generate_quality_report


# =========================================================
# CLARIFICATION
# =========================================================

from query_enrichment.clarification_generator import generate_clarification_plan
from query_enrichment.clarification_processor import run_clarification_processor


# =========================================================
# FILE PATHS
# =========================================================

INPUT = Path("data/query_logs.jsonl")
OUTPUT = Path("data/query_logs_enriched.jsonl")
CLARIFICATION_AUDIT = Path("data/clarification_audit.jsonl")


# =========================================================
# IO HELPERS
# =========================================================

def load_jsonl(path: Path) -> List[Dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def write_jsonl(path: Path, records: List[Dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_clarification_audit(path: Path, records: List[Dict]):
    """
    Stores structured clarification needs for monitoring / analytics.
    """

    audit_rows = []

    for r in records:
        plan = r.get("clarification_plan", {})

        audit_rows.append({
            "query_id": r.get("query_id"),
            "user_query": r.get("user_query"),
            "clarification_required": plan.get("clarification_required", False),
            "num_questions": plan.get("num_questions", 0),
            "missing_dimensions": [
                q["dimension"] for q in plan.get("questions", [])
            ],
            "ambiguity_level": r["interpretation_validation"]["ambiguity_level"],
            "completeness_score": r["interpretation_validation"]["completeness_score"],
            "entity_scope_level": r.get("entity_scope_level"),
            "event_context": r.get("event_context"),
            "retrieval_scope": r.get("retrieval_plan_guidance", {}).get("scope"),
        })

    with path.open("w", encoding="utf-8") as f:
        for row in audit_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


# =========================================================
# INTERPRETATION LAYER
# =========================================================

def interpret_record(r: Dict) -> Dict:

    query = r.get("user_query", "")

    # intent classification
    r["intent"] = r.get("intent") or classify_intent(query)

    # movement direction
    r["movement_direction"] = (
        r.get("movement_direction") or extract_direction(query)
    )

    # operational time range
    r["time_range"] = normalize_time_expression(
        r.get("time_horizon"),
        query
    )

    # hierarchy understanding
    r = resolve_entity_scope(r)

    # event understanding
    r = detect_event_context(r)

    return r


# =========================================================
# MAIN PIPELINE
# =========================================================

# def enrich_query():

#     print("Loading raw query logs...")
#     records = load_jsonl(INPUT)

#     print("Running enrichment...")
#     records = [enrich_record(r) for r in records]

#     print("Running semantic interpretation...")
#     records = [interpret_record(r) for r in records]

#     print("Running interpretation validation...")
#     records = validate_records(records)

#     print("Generating retrieval guidance...")
#     for r in records:
#         meta = r["interpretation_validation"]
#         r["retrieval_plan_guidance"] = recommend_scope(
#             meta["completeness_score"],
#             meta["ambiguity_level"] != "low",
#         )

#     print("Generating clarification plans...")
#     for r in records:
#         r["clarification_plan"] = generate_clarification_plan(r)

#     print("Saving final enriched logs...")
#     write_jsonl(OUTPUT, records)

#     print("Saving clarification audit...")
#     write_clarification_audit(CLARIFICATION_AUDIT, records)

#     print("\nSYSTEM QUALITY REPORT")
#     print(json.dumps(generate_quality_report(records), indent=2))

#     print("\nRunning Clarification Processor")
#     run_clarification_processor()


def enrich_query(last_n: int | None = None):
    """
    Enrich query logs.
    
    Parameters
    ----------
    last_n : int | None
        If provided, only the last N records from INPUT jsonl are processed.
        If None, process all records.
    """

    print("Loading raw query logs...")
    records = load_jsonl(INPUT)

    # ---- select subset from end ----
    if last_n is not None:
        if last_n <= 0:
            raise ValueError("last_n must be a positive integer")
        records = records[-last_n:]
        print(f"Processing last {len(records)} records")

    print("Running enrichment...")
    records = [enrich_record(r) for r in records]

    print("Running semantic interpretation...")
    records = [interpret_record(r) for r in records]

    print("Running interpretation validation...")
    records = validate_records(records)

    print("Generating retrieval guidance...")
    for r in records:
        meta = r["interpretation_validation"]
        r["retrieval_plan_guidance"] = recommend_scope(
            meta["completeness_score"],
            meta["ambiguity_level"] != "low",
        )

    print("Generating clarification plans...")
    for r in records:
        r["clarification_plan"] = generate_clarification_plan(r)

    print("Saving final enriched logs...")
    write_jsonl(OUTPUT, records)

    print("Saving clarification audit...")
    write_clarification_audit(CLARIFICATION_AUDIT, records)

    print("\nSYSTEM QUALITY REPORT")
    print(json.dumps(generate_quality_report(records), indent=2))

    print("\nRunning Clarification Processor")
    run_clarification_processor()