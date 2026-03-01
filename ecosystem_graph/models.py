from pydantic import BaseModel, Field
from typing import Dict, Optional


class GraphNode(BaseModel):
    id: str
    name: str
    node_type: str              # company, sector, macro, commodity
    economic_layer: str         # core, supply, demand, domestic_macro, global
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    source: str = "deterministic"
    metadata: Dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str      # depends_on, influenced_by, drives
    lag_days: Optional[int] = None
    correlation_strength: Optional[float] = None
    causal_confidence: float = 0.0
    evidence_type: str = "structural"