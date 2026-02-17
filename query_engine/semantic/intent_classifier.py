def classify_intent(text):
    t = text.lower()
    if "why" in t:
        return "causal_explanation"
    if "predict" in t or "forecast" in t:
        return "prediction"
    if "compare" in t:
        return "comparison"
    return "analysis"