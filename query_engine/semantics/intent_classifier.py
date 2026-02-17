def classify_intent(query: str):
    q = query.lower()

    if "why" in q or "reason" in q:
        return "causal_explanation"
    if "compare" in q:
        return "comparison"
    if "predict" in q or "forecast" in q:
        return "prediction_request"

    return "general_analysis"