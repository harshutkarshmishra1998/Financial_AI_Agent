def extract_direction(text):
    t = text.lower()
    if any(w in t for w in ["fall", "drop", "decline"]):
        return "down"
    if any(w in t for w in ["rise", "surge", "gain"]):
        return "up"
    return None