import requests
import api_keys

def fetch_fred_series(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_keys.require_env("FRED_API_KEY"),
        "file_type": "json"
    }
    r = requests.get(url, params=params)
    return r.json()
