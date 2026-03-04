# Market Signal Module

The `market_signal` module detects significant market anomalies from OHLCV time series, scores them, clusters nearby events, stores typed artifacts, and exports timelines/plots.

## What this module does
- Downloads historical OHLCV data.
- Engineers volatility and volume-based features.
- Detects anomalies with Isolation Forest.
- Clusters nearby anomaly timestamps into event groups.
- Computes event-level signal strength.
- Writes `AnomalyEvent` artifacts + JSONL timelines.
- Generates analytics plots for quick visual inspection.

## End-to-end flow
1. `run_signal_pipeline(...)` (entrypoint)
2. Calls `engine.run(...)` for data → features → anomaly events.
3. Exports artifacts and JSONL timeline.
4. Produces plot images in `data/<run_id>/plots/`.

## File-by-file reference

### `pipeline.py`
- `run_signal_pipeline(symbol, start, end, run_id)`
  - Orchestrates full signal stage.
  - Calls core engine.
  - Generates these plots:
    - `full_context.png`
    - `anomaly_heatmap.png`
    - `regime_visualizer.png`
    - `signal_vs_volatility.png`
  - Returns event artifact list.

### `engine.py`
- `_safe_price_change(raw, event_date)`
  - Computes close-to-close percent move for event date vs previous day.
  - Returns `0.0` for first row.
- `_cluster_representative(df, cluster)`
  - Picks strongest timestamp inside a cluster using weighted confidence/z-score/volume-z.
- `run(symbol, start, end, run_id)`
  - Main detection engine:
    - fetches data (`fetch_ohlcv`)
    - computes data hash (`foundation.data_hash`)
    - engineers features (`engineer_features`)
    - flags anomalies (`detect_anomalies`)
    - adds rolling DTW similarity (`rolling_dtw`)
    - clusters anomaly days (`cluster_events`)
    - computes event-level signal strength and filters tiny moves
    - builds `AnomalyEvent` objects
    - persists artifacts + exports JSONL files
  - Returns list of anomaly artifacts.

### `data.py`
- `fetch_ohlcv(symbol, start, end)`
  - Pulls OHLCV from Yahoo Finance.
  - Validates required columns (`open/high/low/close/volume`).
  - Flattens MultiIndex columns if present.
  - Enforces sorting, de-duplication, numeric conversion, NA dropping.

### `features.py`
- `engineer_features(df)`
  - Computes:
    - `log_return`
    - rolling mean/std
    - `z_score`
    - `volume_z`
  - Cleans infinities/NaNs.
  - Requires at least 5 rows after cleaning.
  - Standard-scales key feature columns.

### `detector.py`
- `_normalize_scores(scores)`
  - Min-max maps anomaly score array to 0..1 confidence.
- `detect_anomalies(df)`
  - Fits `IsolationForest` using configured params.
  - Adds columns:
    - `anomaly_score`
    - `confidence`
    - `is_anomaly`

### `cluster.py`
- `cluster_events(df)`
  - Filters to anomaly rows.
  - Groups adjacent anomaly dates if date gap <= `CLUSTER_GAP_DAYS`.
  - Returns list of timestamp clusters.

### `dtw.py`
- `compute_dtw_similarity(series1, series2)`
  - Computes FastDTW distance between two windows.
- `rolling_dtw(df)`
  - Computes a rolling sequence of DTW distances over close prices.

### `export.py`
- `export_events_jsonl(events, run_id, filename='anomalies.jsonl')`
  - Writes event-level JSONL used by downstream research + visualization.
- `export_signal_timeline(df, run_id, filename='signal_timeline.jsonl')`
  - Writes row-level timeline JSONL with engineered features/anomaly labels.

### `advanced_plots.py`
- `_load_timeline(run_id)`
  - Loads timeline JSONL into date-indexed DataFrame.
- `multi_symbol_overlay(run_ids)`
  - Scatter comparison of anomaly signal strengths across runs.
- `anomaly_heatmap(run_id)`
  - Monthly mean confidence heatmap.
- `regime_visualizer(run_id, threshold=0.7)`
  - Binary high-volatility regime line plot from confidence threshold.
- `signal_vs_volatility(run_id)`
  - Z-score vs confidence phase scatter.
- `plot_full_signal_context(run_id, symbol=None)`
  - Dual-axis chart (price + signal strength at anomaly timestamps).

### `dashboard.py`
- `four_panel_dashboard(run_id)`
  - Quick Matplotlib dashboard with four vertically stacked signal panels.

### `config.py`
- `ISOLATION_FOREST_PARAMS`: model hyperparameters.
- `FEATURE_WINDOW`: rolling window size.
- `CLUSTER_GAP_DAYS`: max day gap to merge anomalies.
- `MIN_PRICE_MOVE_PCT`: significance filter for event retention.
- `DTW_WINDOW`: DTW comparison window length.

## Practical notes
- If Yahoo returns no data or malformed columns, pipeline stops early with validation error.
- DTW failures are caught in engine; pipeline continues with `NaN` DTW values.
- Exported JSONL files are critical dependencies for `multistream_researcher` and `reasoning` stages.
