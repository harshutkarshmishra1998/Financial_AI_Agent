from datetime import datetime, timedelta


def parse_time(query):

    today = datetime.utcnow().date()

    if "today" in query.lower():
        return {"start": str(today), "end": str(today)}

    if "recent" in query.lower():
        return {
            "start": str(today - timedelta(days=7)),
            "end": str(today),
        }

    return None