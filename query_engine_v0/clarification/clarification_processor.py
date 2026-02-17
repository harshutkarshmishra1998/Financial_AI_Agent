from datetime import datetime, timedelta


def auto_resolve(records):

    today = datetime.utcnow().date()

    for r in records:

        plan = r.get("clarification_plan", {})

        if not plan.get("clarification_required"):
            continue

        if "time_range" in plan["missing_dimensions"]:
            r["time_range"] = {
                "start": str(today - timedelta(days=14)),
                "end": str(today)
            }

        if "movement_direction" in plan["missing_dimensions"]:
            r["movement_direction"] = "down"

        r["clarification_resolved"] = True

    return records