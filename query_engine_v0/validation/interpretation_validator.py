def validate_records(records):

    for r in records:

        score = 0

        if r.get("primary_asset"):
            score += 0.3
        if r.get("intent"):
            score += 0.2
        if r.get("movement_direction"):
            score += 0.2
        if r.get("time_range"):
            score += 0.2
        if r.get("event_context"):
            score += 0.1

        r["interpretation_validation"] = {
            "completeness_score": round(score, 3),
            "ambiguity_level": "low" if score >= 0.7 else "moderate"
        }

    return records