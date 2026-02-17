EVENTS = {
    "earnings": "earnings_release",
    "rate hike": "monetary_policy_change",
}


def detect_event(query):
    q = query.lower()

    for k, v in EVENTS.items():
        if k in q:
            return {"event_type": v}

    return None