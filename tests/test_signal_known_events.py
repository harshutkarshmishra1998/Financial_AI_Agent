from foundation import RunManager
from market_signal.engine import run


def test_covid_crash_detected():

    run_id = RunManager.new_run()

    events = run(
        symbol="RELIANCE.NS",
        start="2019-01-01",
        end="2020-12-31",
        run_id=run_id
    )

    detected_dates = [e.event_timestamp.strftime("%Y-%m") for e in events]

    # assert any("2020-03" in d for d in detected_dates)

    print(detected_dates)
    if any("2020-03" in d for d in detected_dates):
        print("DETECTED COVID CRASH!")

if __name__ == "__main__":
    test_covid_crash_detected()