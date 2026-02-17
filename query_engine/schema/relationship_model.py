from dataclasses import dataclass
from typing import Optional


@dataclass
class AssetRelationship:
    type: Optional[str] = None
    direction: Optional[str] = None
    confidence: float = 0.0