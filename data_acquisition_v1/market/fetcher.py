import uuid
import yfinance as yf #type: ignore

from .processor import process_price_series
from .storage import append_market_record
from .schema import MarketDataRecord

from ..cache_lookup import make_request_hash, find_existing_record
from ..config import MARKET_DATA_PATH


def acquire_market_data(query_id, asset, start, end):

    request_payload = {
        "module": "market",
        "asset": asset,
        "start": start,
        "end": end
    }

    request_hash = make_request_hash(request_payload)

    existing = find_existing_record(MARKET_DATA_PATH, request_hash)

    if existing:
        new_record = existing.copy()
        new_record["record_id"] = str(uuid.uuid4())
        new_record["query_id"] = query_id
        new_record["data_reused"] = True
        new_record["source_record_id"] = existing["record_id"]
        append_market_record(new_record)
        return new_record["record_id"]

    # df = yf.download(asset, start=start, end=end, progress=False)

    df = yf.download(asset, start=start, end=end, progress=False)

    if df is None or df.empty:
        prices, returns, volatility, trend = [], [], 0.0, "no_data"
    else:
        prices, returns, volatility, trend = process_price_series(df)

    # prices, returns, volatility, trend = process_price_series(df)

    record = MarketDataRecord(
        record_id=str(uuid.uuid4()),
        query_id=query_id,
        request_hash=request_hash,
        source_record_id=None,
        asset=asset,
        start=start,
        end=end,
        prices=prices,
        returns=returns,
        volatility=volatility,
        trend=trend,
        data_reused=False
    ).model_dump()

    append_market_record(record)
    return record["record_id"]