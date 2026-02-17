from typing import Dict, Any, List


# =========================================================
# QUESTION TEMPLATES
# =========================================================

TIME_QUESTION = {
    "dimension": "time_range",
    "question": "What time period should I analyze?",
    "options": [
        "today / intraday",
        "last 7 days",
        "last month",
        "last 3 months",
        "last year",
        "since specific event"
    ],
    "priority": 1
}


ASSET_SCOPE_QUESTION = {
    "dimension": "asset_scope",
    "question": "Which specific market or asset group do you mean?",
    "options": [
        "specific company",
        "sector",
        "country market",
        "global market",
        "index"
    ],
    "priority": 1
}


EVENT_QUESTION = {
    "dimension": "event_context",
    "question": "Is this related to a specific event?",
    "options": [
        "earnings release",
        "economic data release",
        "interest rate decision",
        "IPO / corporate action",
        "no specific event"
    ],
    "priority": 2
}


DIRECTION_QUESTION = {
    "dimension": "movement_direction",
    "question": "What type of market movement are you interested in?",
    "options": [
        "price increase",
        "price decline",
        "volatility",
        "general performance"
    ],
    "priority": 2
}


INTENT_QUESTION = {
    "dimension": "intent",
    "question": "What type of analysis do you want?",
    "options": [
        "causal explanation (why it moved)",
        "trend analysis",
        "prediction / outlook",
        "comparison",
        "impact of an event"
    ],
    "priority": 3
}


COMPARISON_QUESTION = {
    "dimension": "comparison_target",
    "question": "What should this be compared against?",
    "options": [
        "previous period",
        "another company",
        "market index",
        "sector average",
        "no comparison"
    ],
    "priority": 3
}


# =========================================================
# MISSING DIMENSION DETECTION
# =========================================================

def detect_missing_dimensions(record: Dict[str, Any]) -> List[Dict]:

    missing = []

    # time clarity
    if not record.get("time_range"):
        missing.append(TIME_QUESTION)

    # entity scope clarity
    if record.get("entity_scope_level") == "single_asset":
        if not record.get("primary_asset"):
            missing.append(ASSET_SCOPE_QUESTION)

    # event context (only if causal query)
    if record.get("intent") == "causal_explanation" and not record.get("event_context"):
        missing.append(EVENT_QUESTION)

    # movement direction
    if not record.get("movement_direction"):
        missing.append(DIRECTION_QUESTION)

    # analytical intent
    if not record.get("intent"):
        missing.append(INTENT_QUESTION)

    # comparison intent
    if record.get("intent") == "comparison" and not record.get("comparison_target"):
        missing.append(COMPARISON_QUESTION)

    return missing


# =========================================================
# PRIORITIZATION
# =========================================================

def prioritize_questions(questions: List[Dict]) -> List[Dict]:
    return sorted(questions, key=lambda q: q["priority"])


# =========================================================
# MAIN GENERATOR
# =========================================================

def generate_clarification_plan(record: Dict[str, Any]) -> Dict[str, Any]:

    missing = detect_missing_dimensions(record)

    if not missing:
        return {
            "clarification_required": False,
            "questions": []
        }

    prioritized = prioritize_questions(missing)

    return {
        "clarification_required": True,
        "num_questions": len(prioritized),
        "questions": prioritized
    }