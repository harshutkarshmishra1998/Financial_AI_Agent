import uuid
import os
import requests
from fredapi import Fred #type: ignore
import api_keys

from .schema import MacroDataRecord
from .storage import append_macro_record

from ..cache_lookup import make_request_hash, find_existing_record
from ..config import MACRO_DATA_PATH


fred = Fred()


def acquire_macro_data(query_id, start, end):

    request_payload = {
        "module": "macro",
        "start": start,
        "end": end
    }

    request_hash = make_request_hash(request_payload)
    existing = find_existing_record(MACRO_DATA_PATH, request_hash)

    if existing:
        new_record = existing.copy()
        new_record["record_id"] = str(uuid.uuid4())
        new_record["query_id"] = query_id
        new_record["data_reused"] = True
        new_record["source_record_id"] = existing["record_id"]
        append_macro_record(new_record)
        return new_record["record_id"]

    indicators = {
        "interest_rate": float(fred.get_series_latest_release("FEDFUNDS").iloc[-1]),
        "inflation": float(fred.get_series_latest_release("CPIAUCSL").iloc[-1])
    }

    record = MacroDataRecord(
        record_id=str(uuid.uuid4()),
        query_id=query_id,
        request_hash=request_hash,
        source_record_id=None,
        start=start,
        end=end,
        indicators=indicators,
        data_reused=False
    ).model_dump()

    append_macro_record(record)
    return record["record_id"]