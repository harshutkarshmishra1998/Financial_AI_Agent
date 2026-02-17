import re
import dateparser #type: ignore
from .config import TIME_BUCKETS

YEAR_PATTERN = r"\b(19|20)\d{2}\b"


def detect_time_horizon(text: str):
    text_lower = text.lower()

    for bucket, keywords in TIME_BUCKETS.items():
        if any(k in text_lower for k in keywords):
            return bucket

    if re.search(YEAR_PATTERN, text):
        return "explicit_year"

    parsed = dateparser.parse(text)
    if parsed:
        return "explicit_date"

    return None