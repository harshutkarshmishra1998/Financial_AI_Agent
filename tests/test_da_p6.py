from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline


query = {
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",
    "interpretation_validation.completeness_score": 0.9
}

print("\n===== FULL MULTI-DOMAIN ACQUISITION TEST =====")

# -------------------------------------------------
# PLAN
# -------------------------------------------------
planner = AcquisitionPlanner()
plan = planner.build_plan(query)

print("\nPLAN:")
print(plan)

# -------------------------------------------------
# EXECUTE PIPELINE
# -------------------------------------------------
pipeline = MultiDomainAcquisitionPipeline()
result = pipeline.run(plan)

# -------------------------------------------------
# OUTPUT
# -------------------------------------------------
print("\nPIPELINE SUCCESS:", result.success)

print("\nEXECUTION LOG:")
for record in result.execution_log:
    print(record)

print("\nDOMAIN RESULTS:")

for domain, data in result.domain_results.items():

    print("\nDOMAIN:", domain)

    if not data:
        print("No data returned")
        continue

    for ticker, info in data.items():
        print("Ticker:", ticker)
        print("Source:", info["source"])
        print("Rows:", info["rows"])
        print("Attempts:", info["attempts"])
        print(info["data"].head())