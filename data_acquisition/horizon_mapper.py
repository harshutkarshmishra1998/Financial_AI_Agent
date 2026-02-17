from datetime import datetime, timedelta
from .config import TIME_HORIZON_TO_DAYS


def resolve_date_range(time_horizon: str):
    days = TIME_HORIZON_TO_DAYS.get(time_horizon, 30)

    end = datetime.utcnow().date()
    start = end - timedelta(days=days)

    return str(start), str(end)