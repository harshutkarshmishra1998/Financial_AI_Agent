from data_acquisition.pipeline.main_acquisition_runner import process_last_n_queries


print("\n===== MAIN ACQUISITION RUNNER TEST =====")

results = process_last_n_queries(50)

print("\nRESULT SUMMARY")
for r in results:
    print(r)