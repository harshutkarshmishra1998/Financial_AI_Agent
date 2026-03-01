from pathlib import Path

DATA_ROOT = Path("data")
DATA_ROOT.mkdir(exist_ok=True)

SCHEMA_VERSION = "1.0.0"

# run tracking database
RUN_DB = DATA_ROOT / "run_metadata.sqlite"

# schema registry file (prevents silent drift)
SCHEMA_REGISTRY = DATA_ROOT / "schema_registry.json"