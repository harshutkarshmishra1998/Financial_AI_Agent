import json
import os
import api_keys
from openai import OpenAI

class LLMDriverRanker:
    """
    Uses an LLM to rank graph nodes so only the most relevant drivers
    are expanded into web search queries.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = None
        self.client = OpenAI()


    def rank(self, anomaly, graph_nodes, top_k: int = 5):
        if not graph_nodes:
            return []

        if self.client is None:
            return graph_nodes[:top_k]

        prompt = f"""
You are a financial causal analyst.

A stock anomaly occurred.

Symbol: {anomaly.get('symbol', '')}
Date: {anomaly.get('timestamp', '')}

Below is a list of possible economic drivers from the company ecosystem.

Select the MOST LIKELY drivers that could explain the market move.
Return only the driver names ranked by relevance.

Drivers:
{', '.join(graph_nodes)}

Return JSON list only.
"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = (resp.choices[0].message.content or "").strip()
            selected = json.loads(content)
            if not isinstance(selected, list):
                return graph_nodes[:top_k]

            selected_lower = {str(node).lower() for node in selected}
            filtered = [node for node in graph_nodes if node.lower() in selected_lower]

            if not filtered:
                return graph_nodes[:top_k]

            return filtered[:top_k]
        except Exception:
            return graph_nodes[:top_k]

