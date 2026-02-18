import os
import requests
import api_keys  # ensures .env loaded


BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(series_id, start=None, end=None):

    api_key = os.getenv("FRED_API")
    if not api_key:
        return []

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }

    if start:
        params["observation_start"] = start
    if end:
        params["observation_end"] = end

    try:
        r = requests.get(BASE_URL, params=params, timeout=20).json()
        return r.get("observations", [])
    except Exception:
        return []