from typing import Dict, Any, List
from openai import OpenAI
import api_keys


# =========================================================
# OPENAI CLIENT
# =========================================================

client = OpenAI()

LLM_MODEL = "gpt-4.1-mini"
LLM_CONFIDENCE_THRESHOLD = 0.6


# =========================================================
# NULL DETECTION
# =========================================================

def find_missing_fields(record: Dict[str, Any]) -> List[str]:
    missing = []
    for k, v in record.items():
        if v is None or v == "" or v == []:
            missing.append(k)
    return missing


# =========================================================
# DETERMINISTIC RESOLUTION (EDITABLE REGISTRIES)
# =========================================================

COMPANY_TO_TICKER = {
    "tesla": "TSLA",
    "apple": "AAPL",
    "reliance": "RELIANCE.NS",
}

TICKER_TO_COUNTRY = {
    "TSLA": "USA",
    "AAPL": "USA",
    "RELIANCE.NS": "India",
}

TICKER_TO_ASSET_CLASS = {
    "TSLA": "equity",
    "AAPL": "equity",
    "RELIANCE.NS": "equity",
}


def deterministic_resolve(record: Dict[str, Any]) -> Dict[str, Dict]:

    resolved = {}
    query = record.get("user_query", "").lower()
    ticker = record.get("ticker")

    # ticker from company mention
    if not ticker:
        for name, symbol in COMPANY_TO_TICKER.items():
            if name in query:
                resolved["ticker"] = {
                    "value": symbol,
                    "source": "deterministic",
                    "confidence": 1.0,
                }
                ticker = symbol
                break

    # country from ticker
    if ticker and not record.get("country"):
        c = TICKER_TO_COUNTRY.get(ticker)
        if c:
            resolved["country"] = {
                "value": c,
                "source": "deterministic",
                "confidence": 1.0,
            }

    # asset class from ticker
    if ticker and not record.get("asset_class"):
        ac = TICKER_TO_ASSET_CLASS.get(ticker)
        if ac:
            resolved["asset_class"] = {
                "value": ac,
                "source": "deterministic",
                "confidence": 1.0,
            }

    return resolved


# =========================================================
# LLM STRUCTURED INFERENCE
# =========================================================

LLM_SYSTEM_PROMPT = """
You are a financial query interpretation engine.

Rules:
- Only infer fields when reasonably certain.
- If uncertain return null.
- Do NOT guess ticker.
- Do NOT invent country.
- Output STRICT JSON only.
"""


def llm_infer(record: Dict[str, Any], missing_fields: List[str]) -> Dict[str, Dict]:

    payload = {
        "user_query": record.get("user_query"),
        "known_fields": record,
        "missing_fields": missing_fields,
    }

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Infer missing semantic fields.

Return format:
{{
  "field": {{
    "value": "...",
    "confidence": 0.0-1.0
  }}
}}

INPUT:
{payload}
"""
            }
        ],
    )

    raw = response.choices[0].message.content
    parsed = {}

    if not raw:
        return parsed

    import json
    data = json.loads(raw)

    for field, info in data.items():
        if not isinstance(info, dict):
            continue

        value = info.get("value")
        confidence = info.get("confidence", 0)

        if value is None:
            continue

        if confidence < LLM_CONFIDENCE_THRESHOLD:
            continue

        parsed[field] = {
            "value": value,
            "source": "llm",
            "confidence": confidence,
        }

    return parsed


# =========================================================
# APPLY RESOLUTIONS
# =========================================================

def apply_resolutions(record: Dict[str, Any], updates: Dict[str, Dict]):

    if "enrichment_meta" not in record:
        record["enrichment_meta"] = {}

    for field, meta in updates.items():
        record[field] = meta["value"]
        record["enrichment_meta"][field] = meta

    return record


# =========================================================
# MAIN ENRICHMENT FUNCTION
# =========================================================

def enrich_record(record: Dict[str, Any]) -> Dict[str, Any]:

    missing = find_missing_fields(record)
    if not missing:
        return record

    # ---------------------------
    # tier 1 — deterministic
    # ---------------------------
    deterministic = deterministic_resolve(record)
    record = apply_resolutions(record, deterministic)

    # recompute missing
    missing = find_missing_fields(record)

    # ---------------------------
    # tier 2 — LLM inference
    # ---------------------------
    if missing:
        llm_updates = llm_infer(record, missing)
        record = apply_resolutions(record, llm_updates)

    return record