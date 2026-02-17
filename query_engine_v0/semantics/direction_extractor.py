DOWN = ["fall", "drop", "decline", "selloff"]
UP = ["rise", "surge", "gain"]


def extract_direction(query):
    q = query.lower()

    if any(w in q for w in DOWN):
        return "down"
    if any(w in q for w in UP):
        return "up"
    return None