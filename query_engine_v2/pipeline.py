from typing import Dict, List

from query_engine_v2.understanding.pipeline import process_query
from query_engine_v2.enrichment.enrichment_core import enrich_record
from query_engine_v2.enrichment.intent_classifier import classify_intent
from query_engine_v2.enrichment.direction_extractor import extract_direction
from query_engine_v2.enrichment.temporal_normalizer import normalize_time_expression
from query_engine_v2.enrichment.entity_hierarchy_resolver import resolve_entity_scope
from query_engine_v2.enrichment.event_semantic_detector import detect_event_context
from query_engine_v2.enrichment.interpretation_validator import validate_records
from query_engine_v2.enrichment.retrieval_scope_advisor import recommend_scope
from query_engine_v2.enrichment.clarification_generator import generate_clarification_plan


def _interpret_enrichment(record: Dict) -> Dict:
    query = record.get("user_query", "")

    record["intent"] = record.get("intent") or classify_intent(query)
    record["movement_direction"] = record.get("movement_direction") or extract_direction(query)
    record["time_range"] = normalize_time_expression(record.get("time_horizon"), query)

    record = resolve_entity_scope(record)
    record = detect_event_context(record)
    return record


def process_and_enrich_query(user_query: str) -> Dict:
    understanding = process_query(user_query).model_dump()

    record = enrich_record(understanding)
    record = _interpret_enrichment(record)
    record = validate_records([record])[0]

    meta = record["interpretation_validation"]
    record["retrieval_plan_guidance"] = recommend_scope(
        meta["completeness_score"],
        meta["ambiguity_level"] != "low",
    )
    record["clarification_plan"] = generate_clarification_plan(record)

    return record


def process_and_enrich_queries(queries: List[str]) -> List[Dict]:
    return [process_and_enrich_query(query) for query in queries]
