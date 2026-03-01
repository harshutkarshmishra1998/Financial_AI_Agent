from __future__ import annotations

from typing import Dict, List, Optional


class GroqLLM:
    """Optional extractor interface. Default returns empty proposals for safe offline behavior."""

    def propose_related_factors(self, node_name: str, context: Optional[Dict] = None) -> List[Dict]:
        return []
