from openai import OpenAI
import api_keys


client = OpenAI()


def llm_semantic_enrichment(record: dict) -> dict:
    """
    Uses LLM to infer missing semantic fields.
    Only fills if missing.
    """

    query = record["user_query"]

    prompt = f"""
Interpret financial query and infer missing fields.

Return JSON:
intent
movement_direction
time_hint
event_hint

Query: {query}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    data = json.loads(response.choices[0].message.content) #type: ignore

    # fill only missing
    if not record.get("intent"):
        record["intent"] = data.get("intent")

    if not record.get("movement_direction"):
        record["movement_direction"] = data.get("movement_direction")

    if not record.get("event_context") and data.get("event_hint"):
        record["event_context"] = {"event_type": data["event_hint"]}

    return record


def enrich_record(record: dict) -> dict:

    record = llm_semantic_enrichment(record)

    record["enrichment_meta"] = {
        "llm_enriched": True
    }

    return record