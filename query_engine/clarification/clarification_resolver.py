from datetime import datetime, timedelta


def auto_resolve(record):
    if not record.time_range:
        today = datetime.utcnow().date()
        record.time_range = {
            "start": str(today - timedelta(days=14)),
            "end": str(today)
        }