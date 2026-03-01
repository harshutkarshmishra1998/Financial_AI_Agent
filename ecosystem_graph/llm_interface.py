from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from typing import Dict, List, Optional

class GroqLLM:
    """
    LLM wrapper with safe fallback behavior.
    If GROQ_API_KEY is unavailable, methods return empty structures.
    """

    def __init__(self, model: str = "qwen-qwq-32b"):
        self.model = model
        self._client = None
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                from groq import Groq  # local import keeps offline use safe

                self._client = Groq(api_key=api_key)
            except Exception:
                self._client = None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def _json_chat(self, prompt: str, default: Any):
        if not self._client:
            return default

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            text = response.choices[0].message.content or ""
            return json.loads(text)
        except Exception:
            return default

    def propose_related_factors(self, node_name: str, context: Optional[Dict] = None) -> List[Dict]:
        context = context or {}
        prompt = f"""
You are an economic graph extraction system.
Given company node: {node_name}
Context: {json.dumps(context)}

Return STRICT JSON list of additional candidate factors only:
[
  {{"name":"...","type":"macro|commodity|policy|factor","relationship":"influenced_by"}}
]
Do not include explanations.
"""
        data = self._json_chat(prompt, default=[])
        return data if isinstance(data, list) else []

    def extract_company_profile(self, symbol: str, company_name: str, sector: str) -> Dict:
        prompt = f"""
Build a compact economic ecosystem profile for listed company.
Symbol: {symbol}
Company: {company_name}
Sector: {sector}

Return STRICT JSON with this schema:
{{
  "inputs": [{{"name": "..."}}],
  "outputs": [{{"name": "..."}}],
  "competitors": ["..."],
  "input_dependencies": {{
    "<input>": {{
      "producers": ["..."],
      "competing_materials": ["..."],
      "influenced_by": ["..."]
    }}
  }},
  "output_dependencies": {{
    "<output>": {{
      "consumer_sectors": ["..."],
      "competing_products": ["..."],
      "influenced_by": ["..."]
    }}
  }}
}}
Keep answer concise and only JSON.
"""
        default = {
            "inputs": [],
            "outputs": [],
            "competitors": [],
            "input_dependencies": {},
            "output_dependencies": {},
        }
        data = self._json_chat(prompt, default=default)
        return data if isinstance(data, dict) else default
