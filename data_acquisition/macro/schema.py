from pydantic import BaseModel
from typing import Optional, Dict


class MacroDataRecord(BaseModel):
    record_id: str
    query_id: str
    request_hash: str
    source_record_id: Optional[str]

    start: str
    end: str
    indicators: Dict[str, float]

    data_reused: bool