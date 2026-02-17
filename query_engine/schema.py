from typing import TypedDict, Optional, Dict, Any


class QueryRecord(TypedDict, total=False):
    query_id: str
    user_query: str

    # structural
    primary_asset: Optional[str]
    ticker: Optional[str]
    country: Optional[str]
    asset_class: Optional[str]

    # semantics
    intent: Optional[str]
    movement_direction: Optional[str]
    time_range: Optional[Dict]
    event_context: Optional[Dict]
    entity_scope_level: Optional[str]

    # enrichment + scoring
    enrichment_meta: Optional[Dict]
    interpretation_validation: Optional[Dict]
    retrieval_plan_guidance: Optional[Dict]

    # clarification
    clarification_plan: Optional[Dict]
    clarification_resolved: Optional[bool]