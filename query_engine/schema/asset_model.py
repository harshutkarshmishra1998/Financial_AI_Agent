from dataclasses import dataclass
from typing import Optional


@dataclass
class Asset:
    name: str
    ticker: Optional[str] = None
    asset_class: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    resolved: bool = False
    confidence: float = 0.0