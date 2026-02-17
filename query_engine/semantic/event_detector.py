EVENTS = {
    "earnings": "earnings_release",
    "fed": "monetary_policy"
}


def detect_event(text):
    lower = text.lower()
    for k, v in EVENTS.items():
        if k in lower:
            return {"event_type": v}
    return None