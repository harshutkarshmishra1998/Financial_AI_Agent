def generate_clarification_plan(record):

    missing = []

    if not record.get("time_range"):
        missing.append("time_range")

    if not record.get("movement_direction"):
        missing.append("movement_direction")

    if not missing:
        return {"clarification_required": False}

    return {
        "clarification_required": True,
        "missing_dimensions": missing
    }