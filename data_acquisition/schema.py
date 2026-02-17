from pydantic import BaseModel
from typing import List


class DataAcquisitionOutput(BaseModel):
    processed_queries: int

    market_records: List[str]
    macro_records: List[str]
    news_records: List[str]
    flow_records: List[str]