from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from multistream_researcher.controller import Phase3Researcher

anomaly = {
    "timestamp": "2022-05-17",
    "symbol": "RELIANCE.NS"
}

graph_nodes = [
    "Crude Oil",
    "OPEC Production",
    "USD INR",
    "RBI Repo Rate",
    "Fuel Tax"
]

def main():
    agent = Phase3Researcher()
    agent.ingest(anomaly, graph_nodes)

    results = agent.retrieve("reason for stock move")

    for r in results:
        print("-" * 80)
        print(r[:400])


if __name__ == "__main__":
    main()
