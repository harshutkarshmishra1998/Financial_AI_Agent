from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline


query = {
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",
    "interpretation_validation.completeness_score": 0.9
}

print("\n===== FULL MULTI-DOMAIN WITH NEWS =====")

planner = AcquisitionPlanner()
plan = planner.build_plan(query)

print("\nPLAN:", plan)

pipeline = MultiDomainAcquisitionPipeline()
result = pipeline.run(plan)

print("\nEXECUTION LOG")
for r in result.execution_log:
    print(r)

print("\nDOMAIN OUTPUTS")

for domain, data in result.domain_results.items():

    print("\n---", domain, "---")

    if domain == "news":
        for asset, articles in data.items():
            print(asset, "articles:", len(articles))
            print(articles[0] if articles else None)

    if domain == "market":
        for asset, info in data.items():
            print(asset, "rows:", info["rows"])