# Reasoning Module

The `reasoning` module turns structured artifacts (signal anomaly, graph, multistream datasets) into a single LLM prompt and produces final narrative reasoning about why the anomaly may have occurred.

## What this module does
- Loads all required run artifacts into a normalized context object.
- Computes graph structural metrics and lightweight tabular summaries.
- Builds a constrained reasoning prompt.
- Calls LLM to generate explanatory text.

## Main pipeline
### `pipeline.py`
- `generate_anomaly_reasoning(run_dir)`
  - Loads `RunContext` via `load_run_context`.
  - Computes graph features for anomaly symbol.
  - Summarizes stock/macro/news streams.
  - Builds prompt.
  - Returns model-generated reasoning text.

## Context assembly
### `context.py`
- `RunContext` dataclass
  - Bundles all stage outputs required for reasoning:
    - run path, anomaly, graph, stock/macro/news rows, manifest.
- `_load_anomaly(run_dir)`
  - Loads anomalies JSONL and returns latest event.
- `_load_graph(run_dir)`
  - Loads ecosystem graph GraphML.
- `_extract_content_rows(df, source)`
  - Normalizes `content` column values into JSON-like dict rows.
  - Handles dict, JSON string, and primitive values safely.
- `_load_multistream(run_dir)`
  - Reads `stock.parquet`, `macro.parquet`, `news.parquet`, then extracts content rows.
- `_load_manifest(run_dir)`
  - Loads `multistream/manifest.json`.
- `load_run_context(run_dir)`
  - Validates directory and returns fully populated `RunContext`.

## Feature and summary computation
### `features.py`
- `extract_graph_features(graph, symbol)`
  - Computes centrality + pagerank for symbol.
  - Captures inbound/outbound edges with relation metadata.
- `summarize_stock(df)`
- `summarize_macro(df)`
  - For numeric columns, returns mean/min/max summary stats.
- `summarize_news(df)`
  - Returns row count and mean for numeric columns.

## Prompt design
### `prompt_builder.py`
- `MAX_PROMPT_CHARS`
  - Hard size cap to reduce oversized context failures.
- `build_prompt(anomaly, graph_features, stock_summary, macro_summary, news_summary)`
  - Prepends strict reasoning instructions.
  - Appends JSON payload with all structured inputs.
  - Raises error if prompt exceeds max size.

## LLM execution
### `llm_interface.py`
- `generate_reasoning_text(prompt)`
  - Sends prompt to Groq chat model (`qwen/qwen3-32b`) and returns generated content.

## Practical notes
- Reasoning quality depends heavily on earlier stages producing complete artifacts.
- If the anomaly symbol is missing from graph, `extract_graph_features` will fail fast.
- Summarizers are intentionally lightweight/statistical (no forecasting or complex causal inference done here).
