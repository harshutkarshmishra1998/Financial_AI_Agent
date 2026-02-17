from pydantic import BaseModel
from typing import Optional, List


class ResolvedAsset(BaseModel):
    name: Optional[str] = None
    ticker: Optional[str] = None
    asset_type: Optional[str] = None
    exchange: Optional[str] = None
    resolved: bool = False
    resolution_method: Optional[str] = None
    score: float = 0.0


class AssetResolutionResult(BaseModel):
    assets: List[ResolvedAsset]
    primary_asset: Optional[ResolvedAsset] = None
    confidence: float = 0.0
    ambiguous: bool = False