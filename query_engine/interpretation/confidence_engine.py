def compute_confidence(assets, intent, time_range):
    score = 0
    if assets:
        score += 0.4
    if intent:
        score += 0.3
    if time_range:
        score += 0.3
    return score