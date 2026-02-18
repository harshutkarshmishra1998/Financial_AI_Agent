from pathlib import Path
import json
from typing import List, Dict, Any

from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline


# =========================================================
# CONFIG — QUERY LOG LOCATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# change if needed
QUERY_LOG_PATH = PROJECT_ROOT / "data" / "query_logs_cleaned.jsonl"


# =========================================================
# QUERY LOG LOADER
# =========================================================

def _load_query_logs() -> List[Dict[str, Any]]:
    """
    Supports JSONL query logs.
    Each line must be a JSON object.
    """

    if not QUERY_LOG_PATH.exists():
        raise FileNotFoundError(f"Query log not found: {QUERY_LOG_PATH}")

    queries = []

    with open(QUERY_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            queries.append(json.loads(line))

    return queries


# =========================================================
# MAIN PROCESSING FUNCTION (PUBLIC API)
# =========================================================

def process_last_n_queries(n: int) -> List[Dict[str, Any]]:
    """
    Run acquisition pipeline for last N query logs.

    Parameters
    ----------
    n : int
        Number of most recent query log entries to process.

    Returns
    -------
    List of execution summaries.
    """

    if n <= 0:
        raise ValueError("n must be > 0")

    queries = _load_query_logs()

    if not queries:
        return []

    selected = queries[-n:]

    planner = AcquisitionPlanner()
    pipeline = MultiDomainAcquisitionPipeline()

    results_summary = []

    for query in selected:

        query_id = query.get("query_id")

        print("\n=================================================")
        print("Processing query:", query_id or "NO_ID")

        try:
            # ---------------------------
            # PLAN
            # ---------------------------
            plan = planner.build_plan(query)

            # ---------------------------
            # EXECUTE
            # ---------------------------
            result = pipeline.run(plan, query=query)

            # ---------------------------
            # SUMMARY RECORD
            # ---------------------------
            summary = {
                "query_id": getattr(result, "query_id", query_id),
                "success": result.success,
                "domains_executed": list(result.domain_results.keys()),
                "execution_log": [
                    {
                        "domain": r.domain,
                        "success": r.success,
                        "message": r.message,
                    }
                    for r in result.execution_log
                ]
            }

        except Exception as e:
            summary = {
                "query_id": query_id,
                "success": False,
                "error": str(e)
            }

        results_summary.append(summary)

    return results_summary