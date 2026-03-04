from pathlib import Path
from reasoning.pipeline import generate_anomaly_reasoning

out = generate_anomaly_reasoning(Path("data/run_1462fceff3c4"))
print(out)