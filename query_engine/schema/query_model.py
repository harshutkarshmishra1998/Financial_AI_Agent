from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .asset_model import Asset
from .relationship_model import AssetRelationship


@dataclass
class QueryInterpretation:
    query_id: str
    user_query: str

    assets: List[Asset] = field(default_factory=list)
    primary_asset: Optional[Asset] = None
    relationship: Optional[AssetRelationship] = None

    intent: Optional[str] = None
    movement_direction: Optional[str] = None
    time_range: Optional[Dict] = None
    event_context: Optional[Dict] = None

    enrichment_meta: Dict = field(default_factory=dict)
    confidence: float = 0.0
    completeness: float = 0.0
    ambiguity: str = "unknown"

    retrieval_scope: Optional[str] = None
    clarification_required: bool = False