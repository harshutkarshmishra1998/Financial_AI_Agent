from foundation import RunManager
from market_signal.pipeline import run_signal_pipeline

from ecosystem_graph.pipeline import EcosystemPipeline
from multistream_researcher.pipeline import run_multistream_researcher


SYMBOL = "RELIANCE.NS"
START = "2019-01-01"
END = "2024-01-01"
RUN_ID = RunManager.new_run()

print(f"Run ID → {RUN_ID}")

print("Running market signal and detecting anomalies...")
events = run_signal_pipeline(
    symbol=SYMBOL,
    start=START,
    end=END,
    run_id=RUN_ID
)

print("Running ecosystem pipeline to understand the impact of detected events...")
ecosystem = EcosystemPipeline("universe/market_universe.parquet", run_id=RUN_ID)
nodes, edges = ecosystem.run(SYMBOL)

print("Executing Multistream Research to ingest required data for research...")
run_multistream_researcher(RUN_ID)



