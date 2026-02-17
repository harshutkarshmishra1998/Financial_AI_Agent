def needs_clarification(record):
    if record.ambiguity != "low":
        return True
    return False