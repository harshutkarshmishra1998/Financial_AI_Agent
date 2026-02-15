from pydantic import BaseModel
from typing import Optional, List


class AssetInfo(BaseModel):
    name: Optional[str] = None
    ticker: Optional[str] = None
    asset_type: Optional[str] = None
    exchange: Optional[str] = None
    resolved: bool = False
    resolution_method: Optional[str] = None
    score: float = 0.0


class QueryUnderstandingOutput(BaseModel):
    query_id: str
    user_query: str
    query_semantics: str

    assets: List[AssetInfo]
    primary_asset: Optional[AssetInfo]

    resolution_confidence: float
    resolution_ambiguous: bool

    relationship_type: str
    relationship_direction: Optional[str]
    relationship_confidence: float

    question_type: str
    time_horizon: Optional[str]
    prediction_requested: bool