# Multistream Researcher Module

The `multistream_researcher` module converts anomaly + graph context into evidence streams (news, macro, stock-like rows) and a retrieval-ready text corpus for downstream reasoning.

## What this module does
- Loads latest anomaly and ecosystem graph for a run.
- Uses an LLM ranker to prioritize graph nodes most relevant to anomaly.
- Saves a filtered subgraph of selected drivers.
- Builds three data streams in `data/<run_id>/multistream/`:
  - `news.parquet`
  - `macro.parquet`
  - `stock.parquet`
  - plus `manifest.json`
- Builds text chunks with metadata for retrieval via `Phase3Researcher`.

## Main orchestration
### `pipeline.py`
- `_save_filtered_graph_artifacts(run_dir, selected_nodes, graph_edges)`
  - Constructs selected-node subgraph.
  - Saves GraphML + pickle snapshots.
- `run_multistream_researcher(run_id)`
  - Reads latest anomaly from signal JSONL.
  - Loads full ecosystem graph.
  - Ranks/selects drivers via `LLMDriverRanker`.
  - Saves filtered graph artifacts.
  - Builds stream parquet artifacts via `MultiStreamArtifactBuilder`.
  - Runs `Phase3Researcher.ingest(...)` to prepare retrieval corpus.

## Retrieval controller
### `controller.py`
- `Phase3Researcher.__init__()`
  - Initializes text store + metadata and LLM ranker.
- `ingest(anomaly_event, graph_nodes)`
  - Ranks graph nodes (fallback to first 6 if ranker fails).
  - Builds web queries.
  - Fetches docs from web connector.
  - Applies fallback synthetic doc if no docs found.
  - Cleans text and chunks it.
  - Stores chunk text and metadata (`url`, `matched_nodes`, `credibility`).
- `_score_text(text, query_tokens)`
  - Token-frequency relevance scoring.
- `retrieve(query)`
  - Returns top 5 chunks ranked by token overlap score.

## LLM node ranking
### `llm_driver_ranker.py`
- `LLMDriverRanker`
  - Uses OpenAI chat completion to pick most likely causal nodes.
- `rank(anomaly, graph_nodes, top_k=5)`
  - Prompts model with anomaly + candidate nodes.
  - Expects JSON list of selected drivers.
  - Filters against original node set.
  - Robustly falls back to first `top_k` nodes on any failure.

## Query construction
### `query_builder.py`
- `build_queries(anomaly_event, graph_nodes, window_days=7)`
  - Generates search templates per node and month of anomaly date.
  - Adds symbol-specific stock movement query when symbol exists.

## Data connectors and preprocessing
### `news_connectors/web_connector.py`
- `_get_search_tool()`
  - Returns LangChain search tool instance (or `None` on failure).
- `search_and_load(query, max_results=5)`
  - Runs web search, normalizes results into `{content, url}` list.
  - Includes robust fallback behavior if tooling/network fails.

### `news_connectors/rss_connector.py`
- `fetch_rss(url)`
  - Reads RSS feed and returns parsed entries.

### `macro_connectors/world_bank.py`
- `fetch_world_bank(indicator)`
  - Fetches indicator payload from World Bank API.

### `macro_connectors/fred.py`
- `fetch_fred_series(series_id)`
  - Fetches FRED series observations with API key support.

### `cleaners/financial_text_cleaner.py`
- `clean_text(text)`
  - Basic text cleaning/normalization for retrieval quality.

### `chunking/domain_chunker.py`
- `chunk_text(text)`
  - Splits cleaned text into manageable chunks.

## Artifact generation
### `storage/artifact_builder.py`
- `_safe_write_parquet(df, path)`
  - Writes parquet; if engine unavailable, writes JSON fallback to same path + marker file.
- `_keywords_to_indicator(node)`
  - Maps node keywords to macro indicator codes.
- `_extract_symbols(graph_nodes, anomaly_symbol=None)`
  - Regex extracts ticker-like tokens from node strings.
- `_synthetic_price(symbol)`
  - Deterministic pseudo-quote generator from hashed symbol.
- `MultiStreamArtifactBuilder`
  - `_build_news_df(anomaly_event, graph_nodes)`
  - `_build_macro_df(graph_nodes)`
  - `_build_stock_df(anomaly_event, graph_nodes)`
  - `build(anomaly_event, graph_nodes)` writes all datasets + manifest.

## Demo entrypoint
### `example_run.py`
- `main()`
  - Demonstrates artifact builder + retriever usage with sample anomaly and graph nodes.

## Practical notes
- This module is intentionally resilient: almost every external dependency has a fallback path.
- `manifest.json` is the canonical pointer file consumed by reasoning stage context loading.
