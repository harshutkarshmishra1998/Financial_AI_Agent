import uuid
import os
import requests
import api_keys

from .schema import NewsRecord
from .storage import append_news_record

from ..cache_lookup import make_request_hash, find_existing_record
from ..config import NEWS_DATA_PATH


def acquire_news_data(query_id, assets, start, end):

    query = " OR ".join(assets)

    payload = {
        "module": "news",
        "query": query,
        "start": start,
        "end": end
    }

    request_hash = make_request_hash(payload)
    existing = find_existing_record(NEWS_DATA_PATH, request_hash)

    if existing:
        new_record = existing.copy()
        new_record["record_id"] = str(uuid.uuid4())
        new_record["query_id"] = query_id
        new_record["data_reused"] = True
        new_record["source_record_id"] = existing["record_id"]
        append_news_record(new_record)
        return new_record["record_id"]

    url = "https://newsapi.org/v2/everything"

    res = requests.get(url, params={
        "q": query,
        "from": start,
        "to": end,
        "language": "en",
        "pageSize": 20
    }).json()

    titles = [a["title"] for a in res.get("articles", [])]

    sentiment = 0.0  # placeholder for later NLP

    record = NewsRecord(
        record_id=str(uuid.uuid4()),
        query_id=query_id,
        request_hash=request_hash,
        source_record_id=None,
        articles=titles,
        sentiment=sentiment,
        data_reused=False
    ).model_dump()

    append_news_record(record)
    return record["record_id"]