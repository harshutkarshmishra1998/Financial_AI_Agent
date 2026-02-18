from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.market_data.market_fetcher import MarketDataFetcher


query = {
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",
    "interpretation_validation.completeness_score": 0.8
}

print("\n===== PHASE 1+2+3+4 FULL TEST =====")

planner = AcquisitionPlanner()
plan = planner.build_plan(query)

print("\nACQUISITION PLAN")
print(plan)

fetcher = MarketDataFetcher()
result = fetcher.fetch(plan.assets, plan)

print("\nFETCH RESULT SUMMARY")

for ticker, info in result.items():
    print("\nTicker:", ticker)
    print("Source:", info["source"])
    print("Rows:", info["rows"])
    print(info["data"].head())