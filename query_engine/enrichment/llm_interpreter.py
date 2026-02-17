from openai import OpenAI
import api_keys
import json

client = OpenAI()


def llm_enrich(query_text):
    prompt = f"""
Extract financial semantics as JSON:
intent, direction, event_hint

Query: {query_text}
"""

    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(r.choices[0].message.content) #type: ignore