# from typing import Dict, Any, List, Optional


# # =========================================================
# # CONTROLLED VOCABULARIES (EDITABLE)
# # =========================================================

# TIME_HORIZON_MAP = {
#     "intraday": "intraday",
#     "short term": "short_term",
#     "short-term": "short_term",
#     "near term": "short_term",
#     "recent": "short_term",
#     "medium term": "medium_term",
#     "long term": "long_term",
#     "long-term": "long_term",
#     "post ipo": "event_relative",
# }

# MOVEMENT_DIRECTION_ALLOWED = {
#     "up",
#     "down",
#     "increase",
#     "decrease",
#     "bullish",
#     "bearish",
# }

# CAUSAL_RELATION_ALLOWED = {
#     "cause",
#     "impact",
#     "influence",
#     "correlation",
#     "comparison",
# }

# ASSET_CLASS_ALLOWED = {
#     "equity",
#     "commodity",
#     "forex",
#     "crypto",
#     "bond",
#     "index",
#     "etf",
# }


# # =========================================================
# # ASSET CANONICALIZATION
# # =========================================================

# def canonicalize_asset(asset: Any) -> Optional[Dict[str, Any]]:
#     """
#     Converts asset into standard structure.
#     """

#     if asset is None:
#         return None

#     if isinstance(asset, dict):
#         return {
#             "name": asset.get("name"),
#             "ticker": asset.get("ticker"),
#             "asset_class": asset.get("asset_class"),
#             "exchange": asset.get("exchange"),
#             "country": asset.get("country"),
#             "resolution_confidence": asset.get("confidence", 1.0),
#         }

#     # string asset fallback
#     if isinstance(asset, str):
#         return {
#             "name": asset,
#             "ticker": None,
#             "asset_class": None,
#             "exchange": None,
#             "country": None,
#             "resolution_confidence": 0.5,
#         }

#     return None


# # =========================================================
# # SEMANTIC NORMALIZATION
# # =========================================================

# def normalize_time_horizon(value: Optional[str]) -> Optional[str]:
#     if not value:
#         return None
#     v = value.lower().strip()
#     return TIME_HORIZON_MAP.get(v, None)


# def normalize_direction(value: Optional[str]) -> Optional[str]:
#     if not value:
#         return None
#     v = value.lower().strip()
#     if v in MOVEMENT_DIRECTION_ALLOWED:
#         return v
#     return None


# # =========================================================
# # CONTRADICTION DETECTION
# # =========================================================

# def detect_contradictions(record: Dict[str, Any]) -> List[str]:

#     contradictions = []

#     horizon = record.get("time_horizon")
#     direction = record.get("movement_direction")

#     if horizon == "intraday" and direction == "long_term_trend":
#         contradictions.append("intraday_vs_long_term_trend")

#     return contradictions


# # =========================================================
# # AMBIGUITY DETECTION
# # =========================================================

# def detect_ambiguity(record: Dict[str, Any]) -> bool:

#     asset = record.get("primary_asset")
#     intent = record.get("intent")

#     if asset is None:
#         return True

#     if intent is None:
#         return True

#     return False


# # =========================================================
# # COMPLETENESS SCORING
# # =========================================================

# def compute_completeness(record: Dict[str, Any]) -> float:

#     score = 0.0

#     # asset certainty
#     asset = record.get("primary_asset")
#     if asset:
#         score += 0.4

#     # time clarity
#     if record.get("time_horizon"):
#         score += 0.2

#     # movement clarity
#     if record.get("movement_direction"):
#         score += 0.2

#     # intent clarity
#     if record.get("intent"):
#         score += 0.2

#     return round(score, 3)


# # =========================================================
# # VALIDATION CORE
# # =========================================================

# def validate_record(record: Dict[str, Any]) -> Dict[str, Any]:

#     validation_meta = {
#         "ontology_normalized": {},
#         "contradictions": [],
#         "ambiguity_detected": False,
#         "completeness_score": 0.0,
#     }

#     # ------------------------------
#     # normalize time horizon
#     # ------------------------------
#     th = normalize_time_horizon(record.get("time_horizon"))
#     record["time_horizon"] = th
#     validation_meta["ontology_normalized"]["time_horizon"] = th

#     # ------------------------------
#     # normalize movement direction
#     # ------------------------------
#     md = normalize_direction(record.get("movement_direction"))
#     record["movement_direction"] = md
#     validation_meta["ontology_normalized"]["movement_direction"] = md

#     # ------------------------------
#     # canonicalize primary asset
#     # ------------------------------
#     record["primary_asset"] = canonicalize_asset(record.get("primary_asset"))

#     # ------------------------------
#     # canonicalize asset list
#     # ------------------------------
#     if "assets" in record and record["assets"]:
#         record["assets"] = [
#             canonicalize_asset(a) for a in record["assets"]
#         ]

#     # ------------------------------
#     # contradiction detection
#     # ------------------------------
#     contradictions = detect_contradictions(record)
#     validation_meta["contradictions"] = contradictions

#     # ------------------------------
#     # ambiguity detection
#     # ------------------------------
#     validation_meta["ambiguity_detected"] = detect_ambiguity(record)

#     # ------------------------------
#     # completeness score
#     # ------------------------------
#     validation_meta["completeness_score"] = compute_completeness(record)

#     record["interpretation_validation"] = validation_meta

#     return record


# # =========================================================
# # BATCH VALIDATOR
# # =========================================================

# def validate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     return [validate_record(r) for r in records]

from typing import Dict, Any, List


# =========================================================
# COMPLETENESS SCORING (REALISTIC)
# =========================================================

def compute_completeness(record):

    score = 0.0

    # core semantics
    if record.get("primary_asset"):
        score += 0.30

    if record.get("intent"):
        score += 0.20

    if record.get("movement_direction"):
        score += 0.15

    if record.get("time_range"):
        score += 0.15

    # hierarchy grounding (more important than before)
    if record.get("entity_scope_level") and record["entity_scope_level"] != "single_asset":
        score += 0.20   # increased from 0.10

    # event grounding
    if record.get("event_context"):
        score += 0.10

    return round(score, 3)


# =========================================================
# AMBIGUITY (REALISTIC THRESHOLDS)
# =========================================================

def detect_ambiguity_level(score, record):

    contextual_strength = 0

    if record.get("entity_scope_level") != "single_asset":
        contextual_strength += 1

    if record.get("event_context"):
        contextual_strength += 1

    adjusted = score + contextual_strength * 0.05

    # relaxed thresholds (more realistic)
    if adjusted >= 0.7:
        return "low"

    if adjusted >= 0.5:
        return "moderate"

    return "high"


def validate_record(record: Dict[str, Any]) -> Dict[str, Any]:

    completeness = compute_completeness(record)
    ambiguity_level = detect_ambiguity_level(completeness, record)

    record["interpretation_validation"] = {
        "completeness_score": completeness,
        "ambiguity_level": ambiguity_level,
        "contradictions": [],
    }

    return record


def validate_records(records: List[Dict]) -> List[Dict]:
    return [validate_record(r) for r in records]