# signal/cli.py

import argparse
from foundation import RunManager
from .engine import run


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)

    args = parser.parse_args()

    run_id = RunManager.new_run()

    run(args.symbol, args.start, args.end, run_id)


if __name__ == "__main__":
    main()