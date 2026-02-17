from datetime import datetime, timedelta


def infer_time(text):
    t = text.lower()
    today = datetime.utcnow().date()

    if "today" in t:
        return {"start": str(today), "end": str(today)}

    if "recent" in t:
        return {"start": str(today - timedelta(days=7)), "end": str(today)}

    return None