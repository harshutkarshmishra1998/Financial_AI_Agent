def detect_ambiguity(completeness):
    if completeness >= 0.75:
        return "low"
    if completeness >= 0.5:
        return "moderate"
    return "high"