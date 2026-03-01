import json
from groq import Groq
import api_keys


class GroqLLM:

    def __init__(self, model="qwen-qwq-32b"):
        self.client = Groq()
        self.model = model

    def propose_related_factors(self, node_name, context=None):
        prompt = f"""
You are an economic analyst.

List economic, financial, or structural factors that can influence:
{node_name}

Return STRICT JSON list.

Example:
[
    {{
        "name": "Brent Crude Oil",
        "type": "commodity",
        "relationship": "input_cost_driver"
    }}
]
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        text = response.choices[0].message.content
        return json.loads(text) #type: ignore