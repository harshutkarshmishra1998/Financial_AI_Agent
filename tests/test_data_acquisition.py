"""
Phase-1 Data Acquisition Test Runner

Runs process_data_acquisition(n) directly
without LangGraph.

Usage:
    python -m tests.test_data_acquisition
"""

from data_acquisition.pipeline import process_data_acquisition


def main():

    # -----------------------------
    # CHANGE THIS VALUE AS NEEDED
    # -----------------------------
    n = 46

    print("\nRunning Phase-1 Data Acquisition")
    print(f"Processing last {n} query log entries\n")

    result = process_data_acquisition(n)

    print("------ RESULT SUMMARY ------")
    print("Processed queries:", result.processed_queries)
    print("Market records:", result.market_records)
    print("Macro records:", result.macro_records)
    print("News records:", result.news_records)
    print("Flow records:", result.flow_records)
    print("----------------------------\n")

    print("Phase-1 execution completed successfully")


if __name__ == "__main__":
    main()