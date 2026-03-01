# Foundation Layer --- System Infrastructure Specification

## 1. Purpose

The **foundation layer** is the infrastructure core of the financial
intelligence pipeline.\
It provides execution environment, data contracts, storage discipline,
and reproducibility guarantees required for all analytical phases.

This layer performs **no financial intelligence or analysis**.

Its responsibility is to guarantee that every phase:

-   runs independently\
-   produces structured artifacts\
-   is reproducible\
-   is traceable\
-   is auditable\
-   can be validated\
-   can be re-executed deterministically

All higher-level system behavior depends on these guarantees.

------------------------------------------------------------------------

## 2. Design Philosophy

### 2.1 Contract-First Architecture

All inter-phase communication occurs through typed artifact schemas.\
No implicit data sharing is allowed.

### 2.2 Deterministic Execution

Given identical inputs and configuration: - outputs must be identical\
- hashes must match\
- run metadata must be reproducible

### 2.3 Phase Isolation

Each phase is: - independently runnable\
- storage mediated\
- import independent\
- execution scoped to a run_id

### 2.4 Full Lineage Tracking

Every artifact records: - source data identity\
- model used\
- feature configuration\
- generation timestamp

### 2.5 Storage Discipline

All outputs are persisted using standardized formats and directory
structure.

------------------------------------------------------------------------

## 3. Directory Structure

    project_root/

    foundation/
        core.py
        config.py
        __init__.py
        FOUNDATION.md

    tests/
        test_foundation.py

    data/   (runtime generated)

The `data/` directory is runtime storage and is not part of source
control.

------------------------------------------------------------------------

## 4. Runtime Storage Model

All executions are grouped by **run_id**.

    data/
        run_metadata.sqlite
        schema_registry.json

        run_<id>/
            <phase_name>/
                artifact.parquet
                artifact.meta.json

### Storage Guarantees

-   each run has isolated directory\
-   each phase writes only to its directory\
-   no cross-phase overwrites allowed\
-   artifact metadata stored separately\
-   artifact hashes recorded

------------------------------------------------------------------------

## 5. Core System Components

### 5.1 Base Artifact Model

All outputs inherit from a common base structure.

Fields: - run_id --- execution identifier\
- phase --- producing module\
- schema_version --- contract version\
- created_at --- pipeline generation time\
- data_hash --- identity of source dataset\
- model_name --- producing model\
- feature_window --- feature configuration

This ensures complete lineage tracking.

------------------------------------------------------------------------

### 5.2 Domain Artifact Example --- AnomalyEvent

Additional fields: - event_timestamp --- real-world market event time\
- symbol --- asset identifier\
- anomaly_score --- model output\
- price_change_pct --- derived movement

Important distinction: - event_timestamp = market reality\
- created_at = pipeline execution

------------------------------------------------------------------------

### 5.3 Schema Registry

Purpose: prevent silent contract drift.

Behavior: - each schema converted to JSON schema\
- schema hashed\
- stored in registry file\
- if structure changes → runtime error

------------------------------------------------------------------------

### 5.4 Run Manager

Responsible for: - generating unique run identifiers\
- creating run directory\
- registering run in ledger

Run ID format:

    run_<12 hex characters>

------------------------------------------------------------------------

### 5.5 Artifact Store

Central IO abstraction.

Responsibilities: - serialize artifacts to parquet\
- enforce schema validation\
- compute artifact hash\
- record metadata\
- persist sidecar meta file\
- read artifacts back into typed models

Phases must never access filesystem directly.

------------------------------------------------------------------------

### 5.6 Run Ledger (SQLite)

Tables:

**runs** - run_id\
- created_at

**phase_runs** - run_id\
- phase\
- duration_sec\
- rows_written\
- artifact_hash\
- timestamp

Ledger is automatically created if missing.

------------------------------------------------------------------------

### 5.7 Data Hashing

Used to detect input changes and support reproducibility.

------------------------------------------------------------------------

### 5.8 Metadata Sidecar

Each artifact produces:

    artifact.meta.json

Contains: - row count\
- file hash\
- write duration

------------------------------------------------------------------------

## 6. Execution Lifecycle

1.  create run_id\
2.  phase executes\
3.  artifacts constructed\
4.  artifacts validated\
5.  artifacts written\
6.  metadata generated\
7.  ledger updated

------------------------------------------------------------------------

## 7. System Invariants

1.  one run_id per execution scope\
2.  one schema version per artifact batch\
3.  no mixed phase outputs in single file\
4.  artifacts immutable after write\
5.  schema registry must match runtime models\
6.  all writes logged\
7.  lineage must exist

------------------------------------------------------------------------

## 8. Test Framework

Integration test validates full artifact lifecycle.

System must self-heal after full storage wipe.

------------------------------------------------------------------------

## 9. Directory Clearing Utility

Allows removing all contents of runtime storage for clean execution.

------------------------------------------------------------------------

## 10. Failure Protections

-   schema drift protection\
-   dataset identity tracking\
-   automatic DB initialization\
-   artifact hashing\
-   run isolation

------------------------------------------------------------------------

## 11. Rules for New Phases

Every new phase must:

1.  define artifact schema\
2.  register schema\
3.  subclass BaseArtifact\
4.  write only via ArtifactStore\
5.  include lineage metadata\
6.  log execution duration\
7.  use provided run_id\
8.  never bypass storage abstraction

------------------------------------------------------------------------

## 12. Extension Points

Foundation supports: - graph artifacts\
- vector storage\
- experiment comparison\
- replay systems\
- orchestration engines

------------------------------------------------------------------------

## 13. Guarantees

-   reproducibility\
-   auditability\
-   lineage visibility\
-   modular independence\
-   deterministic storage

------------------------------------------------------------------------

## 14. Non-Responsibilities

Foundation does NOT perform: - modeling\
- analysis\
- inference\
- reporting

It is infrastructure only.

------------------------------------------------------------------------

## 15. Completion Criteria

Foundation complete when: - full lifecycle test passes\
- storage reset safe\
- schema registry enforced\
- ledger operational\
- lineage populated

------------------------------------------------------------------------

## 16. Role in System

Foundation is the execution substrate for all intelligence layers.

It transforms the system from prototype into research-grade
infrastructure.
