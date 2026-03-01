# PHASE 1 --- MARKET SIGNAL ENGINE

## Technical Architecture & Development Specification (V1)

------------------------------------------------------------------------

# 1. PURPOSE

Phase‑1 is a deterministic market anomaly detection and regime
characterization engine.

It converts raw market OHLCV time series into:

-   statistically validated anomaly events
-   regime segmentation
-   structural volatility signals
-   temporal clustering of shocks
-   persistent research datasets
-   visualization-ready outputs

Phase‑1 does NOT attempt causal explanation.\
It produces **event candidates and market state structure** for later
reasoning phases.

Primary downstream consumers:

-   Phase‑2 Causal Graph Engine
-   Phase‑3 Explanation Layer
-   Research Diagnostics
-   Market Regime Analytics
-   Cross‑Asset Stress Monitoring

------------------------------------------------------------------------

# 2. HIGH LEVEL PIPELINE

RAW MARKET DATA\
↓\
DATA NORMALIZATION\
↓\
FEATURE ENGINEERING (statistical baseline construction)\
↓\
ANOMALY DETECTION (Isolation Forest)\
↓\
TEMPORAL CLUSTERING (event grouping)\
↓\
PATTERN STRUCTURE ANALYSIS (DTW similarity)\
↓\
SIGNAL CALIBRATION (confidence + economic filter)\
↓\
ARTIFACT STORAGE + EXPORT\
↓\
VISUALIZATION & RESEARCH DIAGNOSTICS

------------------------------------------------------------------------

# 3. CORE DESIGN PRINCIPLES

Deterministic\
Reproducible\
Statistically grounded\
Economically filtered\
Time‑aware\
Regime‑aware\
Offline analyzable\
Phase‑separable

Phase‑1 must never embed causal assumptions.

------------------------------------------------------------------------

# 4. DATA CONTRACTS

## Input

OHLCV time series indexed by trading date.

Required columns:

open\
high\
low\
close\
volume

Frequency assumed: daily (but extensible)

------------------------------------------------------------------------

## Output Event (AnomalyEvent)

Each event represents a statistically abnormal market state.

Fields:

run_id\
phase\
schema_version\
created_at\
symbol\
event_timestamp\
anomaly_score\
price_change_pct\
data_hash\
model_name\
feature_window

------------------------------------------------------------------------

## Output Timeline Dataset

Stored per run.

Each record contains:

date\
close\
log_return\
z_score\
volume_z\
anomaly_score\
confidence\
dtw_similarity\
is_anomaly

This dataset supports all diagnostics and dashboards.

------------------------------------------------------------------------

# 5. MODULE RESPONSIBILITIES

config.py --- statistical control parameters\
data.py --- raw data ingestion\
features.py --- statistical feature construction\
detector.py --- anomaly detection\
dtw.py --- structural similarity measurement\
cluster.py --- temporal grouping\
engine.py --- orchestration\
export.py --- persistence\
advanced_plots.py --- visualization\
dashboard.py --- research diagnostics

------------------------------------------------------------------------

# 6. SIGNAL INTERPRETATION MODEL

An anomaly represents statistical rarity relative to local regime AND
economically meaningful price movement.

Signal confidence is statistical abnormality --- not price magnitude.

------------------------------------------------------------------------

# 7. REGIME MODEL

Market assumed to operate in latent states:

normal\
elevated volatility\
shock\
recovery

Phase‑1 detects boundaries only.

------------------------------------------------------------------------

# 8. PHASE SPACE REPRESENTATION

Z‑score = volatility deviation\
Confidence = anomaly likelihood

center → stable\
outer band → stress\
extreme → shock

------------------------------------------------------------------------

# 9. STORAGE STRUCTURE

data/ run_id/ signal/ anomalies.parquet anomalies.jsonl
signal_timeline.jsonl

------------------------------------------------------------------------

# 10. SYSTEM LIMITATIONS

No causal attribution\
No predictive modeling\
No macro factor integration

------------------------------------------------------------------------

# 11. EXTENSION POINTS FOR V2

Regime persistence\
Markov transitions\
Shock decay\
Volatility clustering\
Event similarity networks\
Cross‑asset synchronization\
Stress index\
Early warning signals

------------------------------------------------------------------------

# 12. CONTRACT WITH PHASE‑2

Phase‑1 detects structure.\
Phase‑2 explains structure.

------------------------------------------------------------------------

# 13. REPRODUCIBILITY GUARANTEES

Versioned runs\
Explicit parameters\
Deterministic outputs

------------------------------------------------------------------------

# 14. DEVELOPMENT PHILOSOPHY

Phase separation is strict.

------------------------------------------------------------------------

# 15. STATUS

Phase‑1 production stable.
