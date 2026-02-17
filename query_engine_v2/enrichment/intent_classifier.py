# from typing import Optional


# INTENT_RULES = {
#     "why": "causal_explanation",
#     "reason": "causal_explanation",
#     "impact": "impact_analysis",
#     "compare": "comparison",
#     "vs": "comparison",
#     "forecast": "prediction_request",
#     "predict": "prediction_request",
#     "trend": "trend_analysis",
#     "volatility": "volatility_analysis",
# }


# def classify_intent(query: str) -> Optional[str]:
#     q = query.lower()

#     for keyword, intent in INTENT_RULES.items():
#         if keyword in q:
#             return intent

#     return None

from typing import Optional
from openai import OpenAI
import api_keys


client = OpenAI()

LLM_MODEL = "gpt-4.1-mini"
CONF_THRESHOLD = 0.65


# ------------------------------
# RULE BASE
# ------------------------------

RULES = {
    "why": "causal_explanation",
    "reason": "causal_explanation",
    "what caused": "causal_explanation",
    "impact": "impact_analysis",
    "effect": "impact_analysis",
    "compare": "comparison",
    "vs": "comparison",
    "forecast": "prediction_request",
    "predict": "prediction_request",
    "trend": "trend_analysis",
    "volatility": "volatility_analysis",
}


def rule_intent(query: str) -> Optional[str]:
    q = query.lower()
    for k, v in RULES.items():
        if k in q:
            return v
    return None


# ------------------------------
# LLM FALLBACK
# ------------------------------

def llm_intent(query: str) -> Optional[str]:

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
Classify financial question intent.

Return JSON:
{
 "intent": one of [
   causal_explanation,
   impact_analysis,
   comparison,
   prediction_request,
   trend_analysis,
   volatility_analysis,
   event_analysis,
   general_information
 ],
 "confidence": 0-1
}
"""
            },
            {"role": "user", "content": query}
        ],
    )

    import json
    data = json.loads(resp.choices[0].message.content) #type:ignore

    if data["confidence"] < CONF_THRESHOLD:
        return None

    return data["intent"]


# ------------------------------
# PUBLIC API
# ------------------------------

def classify_intent(query: str) -> Optional[str]:
    return rule_intent(query) or llm_intent(query)