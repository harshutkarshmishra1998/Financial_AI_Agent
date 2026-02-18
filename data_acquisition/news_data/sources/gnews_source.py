import os
import requests
import api_keys


def fetch_gnews(query: str, from_date=None, to_date=None, max_results=50):

    api_key = os.getenv("GNEWS")
    if not api_key:
        return []

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": query,
        "lang": "en",
        "max": max_results,
        "token": api_key
    }

    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    try:
        r = requests.get(url, params=params, timeout=20).json()
        return r.get("articles", [])
    except Exception:
        return []