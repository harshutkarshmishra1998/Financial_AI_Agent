from pydantic import BaseModel
from typing import List, Optional


class MarketDataRecord(BaseModel):
    record_id: str
    query_id: str
    request_hash: str
    source_record_id: Optional[str]

    asset: str
    start: str
    end: str

    prices: List[float]
    returns: List[float]
    volatility: float
    trend: str

    data_reused: bool