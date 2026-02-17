from pydantic import BaseModel
from typing import List, Optional


class NewsRecord(BaseModel):
    record_id: str
    query_id: str
    request_hash: str
    source_record_id: Optional[str]

    articles: List[str]
    sentiment: float

    data_reused: bool