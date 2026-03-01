import json
from groq import Groq
import api_keys


class GroqExtractor:

    def __init__(self, model="qwen-qwq-32b"):
        self.client = Groq()
        self.model = model

    def extract_candidates(self, company, sector, existing_nodes):
        prompt = f"""
Return STRICT JSON.

Company: {company}
Sector: {sector}
Existing Nodes: {existing_nodes}

Propose additional economically meaningful dependency nodes and edges.

JSON format:
{{
    "nodes":[{{"name":"","type":""}}],
    "edges":[{{"source":"","target":"","relation":""}}]
}}
"""

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.15,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(resp.choices[0].message.content) #type: ignore