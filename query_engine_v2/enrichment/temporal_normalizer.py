# from datetime import datetime, timedelta
# from typing import Optional, Dict


# def normalize_time_expression(text: Optional[str]) -> Optional[Dict]:
#     if not text:
#         return None

#     t = text.lower()
#     today = datetime.utcnow().date()

#     if "intraday" in t:
#         return {
#             "type": "session",
#             "start": str(today),
#             "end": str(today),
#         }

#     if "recent" in t or "short" in t:
#         return {
#             "type": "rolling_window",
#             "start": str(today - timedelta(days=7)),
#             "end": str(today),
#         }

#     if "medium" in t:
#         return {
#             "type": "rolling_window",
#             "start": str(today - timedelta(days=90)),
#             "end": str(today),
#         }

#     if "long" in t:
#         return {
#             "type": "rolling_window",
#             "start": str(today - timedelta(days=365)),
#             "end": str(today),
#         }

#     return None

import re
from datetime import datetime, timedelta
from typing import Optional, Dict

def _recent_default_window():
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    return {
        "type": "rolling_window",
        "start": str(today - timedelta(days=7)),
        "end": str(today),
        "inferred": True
    }


def _range(days: int):
    today = datetime.utcnow().date()
    return {
        "type": "rolling_window",
        "start": str(today - timedelta(days=days)),
        "end": str(today),
    }


def parse_natural_time(query: str) -> Optional[Dict]:

    q = query.lower()

    if "today" in q or "intraday" in q:
        d = datetime.utcnow().date()
        return {"type": "session", "start": str(d), "end": str(d)}

    if "this week" in q:
        return _range(7)

    if "last week" in q:
        return _range(14)

    if "recent" in q:
        return _range(7)

    if "last month" in q:
        return _range(30)

    if "past few months" in q:
        return _range(90)

    if "last year" in q:
        return _range(365)

    if "ytd" in q or "year to date" in q:
        today = datetime.utcnow().date()
        start = datetime(today.year, 1, 1).date()
        return {"type": "calendar_range", "start": str(start), "end": str(today)}

    # numeric pattern (last 10 days)
    m = re.search(r"last (\d+) days", q)
    if m:
        return _range(int(m.group(1)))

    return None


# ------------------------------
# PUBLIC API
# ------------------------------

# def normalize_time_expression(label: Optional[str], query: str) -> Optional[Dict]:

#     # priority 1 → natural language
#     natural = parse_natural_time(query)
#     if natural:
#         return natural

#     # fallback label mapping
#     if not label:
#         return None

#     l = label.lower()
#     if "short" in l:
#         return _range(7)
#     if "medium" in l:
#         return _range(90)
#     if "long" in l:
#         return _range(365)

#     return None

def normalize_time_expression(label, query):

    # explicit natural language first
    natural = parse_natural_time(query)
    if natural:
        return natural

    # implicit time inference
    implicit_markers = [
        "current", "recent", "latest", "now",
        "today", "present", "ongoing", "today's"
    ]

    if any(w in query.lower() for w in implicit_markers):
        return _recent_default_window()

    # fallback label mapping
    if not label:
        return None

    l = label.lower()

    if "short" in l:
        return _recent_default_window()

    if "medium" in l:
        return _range(90)

    if "long" in l:
        return _range(365)

    return None