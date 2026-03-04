# Universe Module

The `universe` module builds the market universe master dataset used by graph construction and symbol-level context lookup.

## What this module does
- Loads raw NSE equity symbol master list.
- Loads NSE classification/industry mapping file.
- Merges and normalizes both datasets.
- Validates each symbol against Yahoo Finance availability.
- Enriches each symbol with metadata and derived tags.
- Writes a parquet universe file.

## File reference
### `build_market_universe.py`

#### Constants
- `EQUITY_MASTER`: path to equity master CSV.
- `CLASSIFICATION`: path to NSE industry mapping CSV.
- `OUTPUT`: target parquet path.
- `TEST_SAMPLE_SIZE`: optional cap for fast test runs.

#### Functions
- `load_equity_master()`
  - Reads NSE equity CSV.
  - Renames columns and adds `.NS` yfinance ticker.
- `load_classification()`
  - Reads classification CSV.
  - Normalizes column names and maps to standardized fields:
    - `nse_industry`, `nse_industry_group`, `nse_subgroup`, `nse_basic_industry`.
  - Ensures required fields exist.
- `generate_exposure_tags(basic_industry)`
  - Rule-based macro/commodity/global exposure tagging by industry text.
- `generate_news_aliases(company, symbol)`
  - Produces search alias terms for company and symbol.
- `fetch_yf_metadata(ticker)`
  - Checks tradability/data existence via Yahoo Finance.
  - Extracts currency, market cap, volume, first trade date.
- `build_universe()`
  - End-to-end builder:
    - load + merge source files
    - optional sample truncation
    - metadata fetch per symbol
    - serialize exposure tags/news aliases as JSON strings
    - set instrument flags
    - save parquet output

## Output schema highlights
Typical columns in final parquet include:
- `symbol`, `company_name`, `isin`, `yfinance_symbol`
- industry hierarchy columns
- market metadata (`currency`, `market_cap`, `avg_daily_volume`, `data_start`)
- `exposure_tags` (JSON string)
- `news_aliases` (JSON string)
- `instrument_type`, `is_active`

## Practical notes
- Yahoo Finance metadata retrieval is the slowest stage in universe generation.
- `build_universe` currently swallows metadata exceptions at per-ticker granularity and skips failures.
- This output is consumed by `ecosystem_graph.data.market_universe.MarketUniverse`.
