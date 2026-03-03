from __future__ import annotations

from groq import Groq
import api_keys

def generate_reasoning_text(prompt: str, context: dict, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Generate reasoning with LLM if API key is available.
    Falls back to deterministic template reasoning otherwise.
    """

    client = Groq()
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a financial anomaly root-cause analyst."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() #type: ignore
