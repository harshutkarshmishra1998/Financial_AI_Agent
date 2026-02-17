from uuid import uuid4
from query_engine.schema.query_model import QueryInterpretation

from query_engine.structural.asset_resolver import resolve_assets
from query_engine.structural.relationship_extractor import extract_relationship

from query_engine.semantic.intent_classifier import classify_intent
from query_engine.semantic.direction_extractor import extract_direction
from query_engine.semantic.temporal_reasoner import infer_time
from query_engine.semantic.event_detector import detect_event

from query_engine.enrichment.llm_interpreter import llm_enrich

from query_engine.interpretation.confidence_engine import compute_confidence
from query_engine.interpretation.completeness_scorer import compute_completeness
from query_engine.interpretation.ambiguity_detector import detect_ambiguity

from query_engine.planning.retrieval_scope_advisor import choose_scope
from query_engine.clarification.clarification_generator import needs_clarification
from query_engine.clarification.clarification_resolver import auto_resolve


def process_query(text):

    q = QueryInterpretation(
        query_id=str(uuid4()),
        user_query=text
    )

    q.assets = resolve_assets(text)
    if q.assets:
        q.primary_asset = q.assets[0]

    q.relationship = extract_relationship(text, q.assets)

    q.intent = classify_intent(text)
    q.movement_direction = extract_direction(text)
    q.time_range = infer_time(text)
    q.event_context = detect_event(text)

    llm_data = llm_enrich(text)
    q.enrichment_meta = llm_data

    q.confidence = compute_confidence(q.assets, q.intent, q.time_range)
    q.completeness = compute_completeness(q)
    q.ambiguity = detect_ambiguity(q.completeness)

    q.retrieval_scope = choose_scope(q.completeness, q.ambiguity)

    q.clarification_required = needs_clarification(q)
    if q.clarification_required:
        auto_resolve(q)

    return q