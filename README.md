# Financial AI Agent

A modular pipeline that detects stock anomalies, constructs a causal ecosystem graph, enriches evidence from multi-source research streams, and generates structured AI reasoning.

## High-level objective
Given a symbol and time window, the project aims to answer:
1. **Did an unusual market move occur?** (signal detection)
2. **What structural drivers may explain it?** (ecosystem graph)
3. **What supporting evidence exists across data streams?** (multistream research)
4. **What is the final explanation narrative?** (reasoning layer)

## Core modules
- **`foundation/`**
  - Run management, typed artifact schemas, parquet persistence, schema registry, run ledger.
- **`market_signal/`**
  - OHLCV ingestion, feature engineering, anomaly detection, event clustering, plotting/export.
- **`ecosystem_graph/`**
  - Industry/macro dependency graph + LLM-assisted expansion and visualization.
- **`multistream_researcher/`**
  - Driver ranking, web/macro/stock stream artifact generation, retrieval corpus preparation.
- **`reasoning/`**
  - Context assembly, feature summarization, prompt building, final LLM reasoning output.
- **`universe/`**
  - Market-universe construction and symbol metadata enrichment.

## Pipeline sequence
1. `RunManager.new_run()` creates run scope.
2. `market_signal` writes anomaly artifacts and timelines.
3. `ecosystem_graph` writes graph outputs.
4. `multistream_researcher` writes stream artifacts and filtered graph.
5. `reasoning` loads all artifacts and returns explanation text.

## Main interfaces
- **Streamlit app**: `app.py`
  - Interactive end-to-end run from UI.
- **CLI placeholder**: `main.py`
- **Tests**: `tests/test_pipeline.py`

## Runtime output layout
Generated under `data/` by `run_id`, e.g.:

```text
data/
  run_<id>/
    signal/
    plots/
    graph_outputs/
    multistream/
```

## Environment and keys
The project loads secrets from `.env` via `api_keys.py`, then maps them into standard environment variable names expected by providers (OpenAI/Groq/FRED/LangChain).

## Why this architecture is useful
- **Traceable**: each run has explicit lineage and persisted outputs.
- **Composable**: modules can be run/tested independently.
- **Auditable**: artifacts are structured and reproducible.
- **Extensible**: new phases can plug into the same run/artifact contracts.

## Documentation map
Each major module now contains its own `README.md` with detailed per-file and per-function explanations:
- `foundation/README.md`
- `market_signal/README.md`
- `ecosystem_graph/README.md`
- `multistream_researcher/README.md`
- `reasoning/README.md`
- `universe/README.md`

For infra design philosophy, also see `foundation/FOUNDATION.md`.
