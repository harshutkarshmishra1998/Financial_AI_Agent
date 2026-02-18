# from data_acquisition.pipeline.main_acquisition_runner import process_last_n_queries


# print("\n===== MAIN ACQUISITION RUNNER TEST =====")

# results = process_last_n_queries(3)

# print("\nRESULT SUMMARY")
# for r in results:
#     print(r)

from data_acquisition.pipeline.main_acquisition_runner import _load_query_logs
from data_acquisition.pipeline.acquisition_planner import AcquisitionPlanner
from data_acquisition.pipeline.acquisition_pipeline import MultiDomainAcquisitionPipeline

queries = _load_query_logs()[-3:]

planner = AcquisitionPlanner()
pipeline = MultiDomainAcquisitionPipeline()

for q in queries:
    print("\nQUERY:", q.get("query_id"))

    plan = planner.build_plan(q)
    result = pipeline.run(plan, query=q)

    print("domains returned:", list(result.domain_results.keys()))

    market_data = result.domain_results.get("market", {})
    print("market assets:", list(market_data.keys()))