from pydantic import BaseModel
from typing import Optional


class FlowRecord(BaseModel):
    record_id: str
    query_id: str
    request_hash: str
    source_record_id: Optional[str]

    asset: str
    flow_direction: str

    data_reused: bool