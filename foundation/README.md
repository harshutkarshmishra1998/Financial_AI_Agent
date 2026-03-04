# Foundation Module

The `foundation` module is the infrastructure backbone for the project. It provides the **run lifecycle**, **artifact schemas**, **storage IO**, and **run metadata logging** used by the rest of the pipeline.

> If you only remember one thing: every pipeline stage should write typed artifacts through `ArtifactStore`, under a unique `run_id`, with traceability captured in SQLite + metadata sidecars.

## What this module does
- Creates and tracks unique run IDs.
- Defines canonical artifact schemas (`BaseArtifact`, `AnomalyEvent`).
- Prevents schema drift through `SchemaRegistry`.
- Persists artifacts as parquet and logs metadata.
- Logs run/phase execution metadata to a SQLite ledger.

## Key files
- `core.py`: all runtime utilities, schema models, storage and ledger implementation.
- `config.py`: canonical storage paths and schema version constants.
- `FOUNDATION.md`: architecture-level specification and design rationale.
- `__init__.py`: convenience exports consumed by downstream modules.

## Detailed behavior by function/class

### `core.py`

#### Utility functions
- `now()`
  - Returns current UTC timestamp (`datetime.utcnow()`), used across artifacts and logs.
- `file_hash(path)`
  - Computes MD5 of a written file for lineage and integrity records.
- `data_hash(df)`
  - Computes a deterministic hash over DataFrame content (via `hash_pandas_object`) to represent source data identity.

#### `SchemaRegistry`
- `register(model)`
  - Builds JSON schema for a Pydantic model.
  - Hashes it and stores signature in `data/schema_registry.json`.
  - Raises runtime error if the same model name is re-registered with a different schema signature (schema drift protection).

#### Artifact models
- `BaseArtifact`
  - Shared metadata contract used by all artifacts:
    - `run_id`, `phase`, `schema_version`, `created_at`
    - lineage fields: `data_hash`, `model_name`, `feature_window`
- `AnomalyEvent(BaseArtifact)`
  - Signal-phase event contract with:
    - `event_timestamp`, `symbol`, `anomaly_score`, `price_change_pct`
  - Registered with `SchemaRegistry` at import time.

#### `RunLedger`
- `init()`
  - Creates `runs` and `phase_runs` tables if missing.
- `log_run(run_id)`
  - Inserts a run-level entry.
- `log_phase(run_id, phase, duration, rows, artifact_hash)`
  - Inserts phase-level execution metrics.

#### `RunManager`
- `new_run()`
  - Generates IDs like `run_<12-hex>`.
  - Creates `data/run_<id>/` directory.
  - Logs run in SQLite.

#### `ArtifactStore`
- `_phase_dir(run_id, phase)`
  - Ensures and returns `data/<run_id>/<phase>/` path.
- `write(artifacts, filename)`
  - Validates non-empty artifact list.
  - Converts Pydantic models to DataFrame.
  - Writes parquet file.
  - Computes file hash and timing.
  - Logs phase metrics in ledger.
  - Writes sidecar metadata JSON (`rows`, `hash`, `duration_sec`).
- `read(run_id, phase, filename, model)`
  - Reads parquet and rehydrates rows into typed Pydantic models.

### `config.py`
- `DATA_ROOT`
  - Root runtime storage directory (`data/`), created automatically.
- `SCHEMA_VERSION`
  - Global schema version used by artifacts (`1.0.0`).
- `RUN_DB`
  - SQLite ledger path (`data/run_metadata.sqlite`).
- `SCHEMA_REGISTRY`
  - Schema signature registry path (`data/schema_registry.json`).

## How other modules should use foundation
1. Create a run with `RunManager.new_run()`.
2. Produce Pydantic artifacts with consistent `run_id` + `phase`.
3. Persist via `ArtifactStore.write(...)`.
4. Read back via `ArtifactStore.read(...)` when needed.

## Caveats and gotchas
- `ArtifactStore.write` expects **non-empty** artifacts.
- Schema changes in a registered model may intentionally break execution until versioning/migration is handled.
- Hashing uses MD5 (good for identity tracking, not cryptographic security guarantees).
