def choose_scope(completeness, ambiguity):
    if completeness > 0.75:
        return "targeted"
    if ambiguity == "moderate":
        return "expanded"
    return "broad"