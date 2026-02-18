from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.market_data.market_fetcher import MarketDataFetcher


query = {
    "assets": [{"ticker": "AAPL"}],
    "user_query": "future outlook for apple",
    "intent": "prediction_request",   # requires 120 rows
    "interpretation_validation.completeness_score": 0.9
}

print("\n===== FULL ADAPTIVE ACQUISITION TEST =====")

planner = AcquisitionPlanner()
plan = planner.build_plan(query)

print("\nPLAN:")
print(plan)

fetcher = MarketDataFetcher()
result = fetcher.fetch(plan.assets, plan)

print("\nRESULT:")

if not result:
    print("No dataset satisfied requirements.")
else:
    for ticker, info in result.items():
        print("\nTicker:", ticker)
        print("Source:", info["source"])
        print("Rows:", info["rows"])
        print("Attempts:", info["attempts"])
        print(info["data"].head())