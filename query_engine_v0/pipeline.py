from uuid import uuid4
from pathlib import Path

from query_engine.io.writer import write_jsonl

from query_engine.parsing.asset_resolver import resolve_assets
from query_engine.semantics.intent_classifier import classify_intent
from query_engine.semantics.direction_extractor import extract_direction
from query_engine.semantics.time_parser import parse_time
from query_engine.semantics.event_detector import detect_event
from query_engine.semantics.hierarchy_resolver import resolve_scope

from query_engine.enrichment.enrichment_core import enrich_record

from query_engine.validation.interpretation_validator import validate_records
from query_engine.validation.quality_reporter import generate_quality_report

from query_engine.clarification.clarification_generator import generate_clarification_plan
from query_engine.clarification.clarification_processor import auto_resolve


FINAL = Path("data/query_logs_final.jsonl")


# =========================================================
# BUILD QUERY LOGS FROM QUERY LIST
# =========================================================

def build_query_logs(queries):

    return [
        {
            "query_id": str(uuid4()),
            "user_query": q
        }
        for q in queries
    ]


# =========================================================
# INTERPRET RECORD
# =========================================================

def interpret_record(record):

    record = resolve_assets(record)

    q = record["user_query"]

    record["intent"] = classify_intent(q)
    record["movement_direction"] = extract_direction(q)
    record["time_range"] = parse_time(q)
    record["event_context"] = detect_event(q)

    record = resolve_scope(record)

    return record


# =========================================================
# FULL ENGINE
# =========================================================

def run_query_engine(queries):

    print("Building query logs...")
    records = build_query_logs(queries)

    print("Interpretation...")
    records = [interpret_record(r) for r in records]

    print("LLM enrichment...")
    records = [enrich_record(r) for r in records]

    print("Validation...")
    records = validate_records(records)

    print("Clarification planning...")
    for r in records:
        r["clarification_plan"] = generate_clarification_plan(r)

    print("Auto clarification resolution...")
    records = auto_resolve(records)

    print("Saving final logs...")
    write_jsonl(FINAL, records)

    print("Quality:", generate_quality_report(records))

    return records