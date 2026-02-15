import uuid
from .schema import QueryUnderstandingOutput, AssetInfo
from .asset_resolver import resolve_assets
from .time_parser import detect_time_horizon
from .intent_classifier import classify_intent
from .forecast_detector import detect_forecast_request
from .storage import append_query_log
from .query_semantics import classify_query_semantics
from .asset_relationships import classify_asset_relationship


def process_query(user_query: str):

    semantics = classify_query_semantics(user_query)
    resolution = resolve_assets(user_query)

    relationship = classify_asset_relationship(
        user_query,
        len(resolution.assets)
    )

    result = QueryUnderstandingOutput(
        query_id=str(uuid.uuid4()),
        user_query=user_query,
        query_semantics=semantics,

        assets=[AssetInfo(**a.model_dump()) for a in resolution.assets],
        primary_asset=AssetInfo(**resolution.primary_asset.model_dump()) if resolution.primary_asset else None,

        resolution_confidence=resolution.confidence,
        resolution_ambiguous=resolution.ambiguous,

        relationship_type=relationship["relationship_type"],
        relationship_direction=relationship["direction"],
        relationship_confidence=relationship["confidence"],

        question_type=classify_intent(user_query),
        time_horizon=detect_time_horizon(user_query),
        prediction_requested=detect_forecast_request(user_query),
    )

    append_query_log(result.model_dump())
    return result