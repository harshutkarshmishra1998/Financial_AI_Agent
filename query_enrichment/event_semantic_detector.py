from typing import Dict, Any, Optional


# =========================================================
# EVENT PATTERNS
# =========================================================

EVENT_PATTERNS = {

    # earnings / corporate
    "earnings": "earnings_release",
    "results": "earnings_release",
    "quarterly results": "earnings_release",
    "guidance": "corporate_guidance",
    "guidance cut": "corporate_guidance_change",
    "guidance raise": "corporate_guidance_change",

    # macro data
    "cpi": "inflation_data_release",
    "inflation data": "inflation_data_release",
    "gdp": "gdp_release",
    "jobs data": "employment_data_release",
    "payrolls": "employment_data_release",

    # central bank
    "rate hike": "monetary_policy_change",
    "rate cut": "monetary_policy_change",
    "interest rate": "monetary_policy_change",
    "fed decision": "central_bank_decision",
    "policy meeting": "central_bank_decision",

    # corporate lifecycle
    "ipo": "ipo_event",
    "listing": "ipo_event",
    "merger": "m&a_event",
    "acquisition": "m&a_event",

    # general event language
    "announcement": "corporate_event",
    "data release": "macro_data_release",
    "report": "data_release",
}


RELATIVE_TIME_MARKERS = {
    "after": "post_event",
    "before": "pre_event",
    "since": "since_event",
    "following": "post_event",
}


# =========================================================
# DETECTOR
# =========================================================

def detect_event_context(record: Dict[str, Any]) -> Dict[str, Any]:

    query = record.get("user_query", "").lower()

    record["event_context"] = None

    detected_event: Optional[str] = None
    relative_position: Optional[str] = None

    # event type
    for phrase, event in EVENT_PATTERNS.items():
        if phrase in query:
            detected_event = event
            break

    if not detected_event:
        return record

    # relative time reference
    for marker, rel in RELATIVE_TIME_MARKERS.items():
        if marker in query:
            relative_position = rel
            break

    record["event_context"] = {
        "event_type": detected_event,
        "temporal_relation": relative_position or "unspecified"
    }

    return record