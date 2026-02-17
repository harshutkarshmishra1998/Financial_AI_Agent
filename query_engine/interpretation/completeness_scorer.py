def compute_completeness(record):
    score = 0
    if record.assets:
        score += 0.3
    if record.intent:
        score += 0.2
    if record.time_range:
        score += 0.2
    if record.event_context:
        score += 0.2
    if record.movement_direction:
        score += 0.1
    return score