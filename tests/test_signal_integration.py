from foundation import RunManager
from market_signal.engine import run


def test_full_signal_run():

    run_id = RunManager.new_run()

    events = run(
        symbol="RELIANCE.NS",
        start="2020-01-01",
        end="2021-01-01",
        run_id=run_id
    )

    # assert isinstance(events, list)
    print(events)

if __name__ == "__main__":
    test_full_signal_run()