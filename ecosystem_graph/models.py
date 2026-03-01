from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    name: str
    node_type: str  # company, sector, commodity, macro, policy...
    economic_layer: str  # core, supply, demand, domestic_macro, global_macro, competition
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    source: str = "deterministic"
    metadata: Dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str  # depends_on, influenced_by, competes_with, produces...
    lag_days: Optional[int] = None
    correlation_strength: Optional[float] = None
    causal_confidence: float = 0.0
    evidence_type: str = "structural"


class GraphBundle(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
