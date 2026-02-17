def generate_quality_report(records):
    total = len(records)
    avg = sum(r["interpretation_validation"]["completeness_score"] for r in records)/total
    return {"total": total, "avg_completeness": round(avg,3)}