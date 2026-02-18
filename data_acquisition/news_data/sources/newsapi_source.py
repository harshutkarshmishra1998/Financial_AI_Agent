import os
import requests
import api_keys

def fetch_newsapi(query: str, from_date=None, to_date=None, page_size=50):

    api_key = os.getenv("NEWS_API")
    if not api_key:
        return []

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": api_key
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