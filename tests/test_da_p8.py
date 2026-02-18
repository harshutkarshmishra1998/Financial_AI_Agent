from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline


query = {
    "query_id": "TEST_QUERY_001",
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",
    "interpretation_validation.completeness_score": 0.9
}

print("\n===== SNAPSHOT STORAGE TEST =====")

planner = AcquisitionPlanner()
plan = planner.build_plan(query)

pipeline = MultiDomainAcquisitionPipeline()
result = pipeline.run(plan, query=query)

print("Pipeline success:", result.success)
print("Query ID:", result.query_id)

print("\nCheck files:")
print("project_root/data/market.jsonl")
print("project_root/data/news.jsonl")