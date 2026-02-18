from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline


query = {
    "query_id": "TEST_MACRO_001",
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",
    "interpretation_validation.completeness_score": 0.9
}

print("\n===== FULL SYSTEM WITH MACRO =====")

planner = AcquisitionPlanner()
plan = planner.build_plan(query)

pipeline = MultiDomainAcquisitionPipeline()
result = pipeline.run(plan, query=query)

print("\nEXECUTION LOG")
for r in result.execution_log:
    print(r)

print("\nMACRO INDICATORS")
macro = result.domain_results.get("macro", {})
for k, v in macro.items():
    print(k, "points:", len(v))