import argparse

from run_agent import run_full_pipeline
from tests.test_foundation import clear_directory


def parse_args():
    parser = argparse.ArgumentParser(description="Run full stock pipeline and persist ecosystem graph")
    parser.add_argument("--symbol", type=str, required=True, help="Ticker symbol (e.g. TCS.NS)")
    parser.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Do not clear existing data/ before running",
    )
    return parser.parse_args()

    print(f"Graph saved: nodes={len(nodes)}, edges={len(edges)} @ {graph_dir}")
    return nodes, edges

if __name__ == "__main__":
    args = parse_args()

    if not args.keep_data:
        clear_directory("data")

    result = run_full_pipeline(
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
    )

    print("\nFULL PIPELINE COMPLETE")
    print(result)
