# from typing import List, Dict


# def generate_quality_report(records: List[Dict]) -> Dict:

#     total = len(records)
#     if total == 0:
#         return {}

#     avg_completeness = sum(
#         r["interpretation_validation"]["completeness_score"]
#         for r in records
#     ) / total

#     ambiguity_rate = sum(
#         1 for r in records
#         if r["interpretation_validation"]["ambiguity_detected"]
#     ) / total

#     return {
#         "total_queries": total,
#         "average_completeness": round(avg_completeness, 3),
#         "ambiguity_rate": round(ambiguity_rate, 3),
#     }

from typing import List, Dict


def generate_quality_report(records: List[Dict]) -> Dict:

    total = len(records)
    if total == 0:
        return {}

    # ------------------------------
    # completeness
    # ------------------------------
    avg_completeness = sum(
        r["interpretation_validation"]["completeness_score"]
        for r in records
    ) / total

    # ------------------------------
    # ambiguity rate
    # (moderate + high considered ambiguous)
    # ------------------------------
    ambiguous = sum(
        1 for r in records
        if r["interpretation_validation"]["ambiguity_level"] != "low"
    )

    ambiguity_rate = ambiguous / total

    # ------------------------------
    # distribution (very useful)
    # ------------------------------
    distribution = {
        "low": 0,
        "moderate": 0,
        "high": 0,
    }

    for r in records:
        level = r["interpretation_validation"]["ambiguity_level"]
        distribution[level] += 1

    return {
        "total_queries": total,
        "average_completeness": round(avg_completeness, 3),
        "ambiguity_rate": round(ambiguity_rate, 3),
        "ambiguity_distribution": distribution,
    }