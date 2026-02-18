import uuid
import yfinance as yf #type: ignore
import pandas as pd

from .schema import FlowRecord
from .storage import append_flow_record

from ..cache_lookup import make_request_hash, find_existing_record
from ..config import FLOW_DATA_PATH


def _extract_volume_series(df: pd.DataFrame):
    """
    Robust volume extractor handling:
    - single ticker
    - multi ticker
    - MultiIndex columns
    - missing data
    """

    if df is None or df.empty:
        return None

    volume_col = None

    # MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        if "Volume" in df.columns.get_level_values(0):
            volume_col = df["Volume"]
            if isinstance(volume_col, pd.DataFrame):
                volume_col = volume_col.iloc[:, 0] #type: ignore

    # Normal columns
    else:
        if "Volume" in df.columns:
            volume_col = df["Volume"]

    if volume_col is None:
        return None

    volume_series = volume_col.dropna()

    if volume_series.empty:
        return None

    return volume_series


def acquire_flow_data(query_id, asset, start, end):

    payload = {
        "module": "flow",
        "asset": asset,
        "start": start,
        "end": end
    }

    request_hash = make_request_hash(payload)
    existing = find_existing_record(FLOW_DATA_PATH, request_hash)

    if existing:
        new_record = existing.copy()
        new_record["record_id"] = str(uuid.uuid4())
        new_record["query_id"] = query_id
        new_record["data_reused"] = True
        new_record["source_record_id"] = existing["record_id"]
        append_flow_record(new_record)
        return new_record["record_id"]

    df = yf.download(asset, start=start, end=end, progress=False)

    volume_series = _extract_volume_series(df)

    if volume_series is None:
        direction = "no_data"
    else:
        latest_volume = float(volume_series.iloc[-1])
        mean_volume = float(volume_series.mean())
        direction = "inflow" if latest_volume > mean_volume else "outflow"

    record = FlowRecord(
        record_id=str(uuid.uuid4()),
        query_id=query_id,
        request_hash=request_hash,
        source_record_id=None,
        asset=asset,
        flow_direction=direction,
        data_reused=False
    ).model_dump()

    append_flow_record(record)
    return record["record_id"]