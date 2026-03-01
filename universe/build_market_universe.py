# import pandas as pd
# import yfinance as yf
# from tqdm import tqdm


# # ============================================
# # PATHS
# # ============================================

# EQUITY_MASTER = "universe/EQUITY_L.csv"
# CLASSIFICATION = "universe/ind_nifty500list.csv"
# OUTPUT = "universe/market_universe.parquet"


# # ============================================
# # LOAD DATA
# # ============================================

# equity = pd.read_csv(EQUITY_MASTER)
# equity = equity.rename(columns={
#     "SYMBOL": "symbol",
#     "NAME OF COMPANY": "company_name",
#     " ISIN NUMBER": "isin"
# })

# equity["yfinance_symbol"] = equity["symbol"] + ".NS"


# industry = pd.read_csv(CLASSIFICATION)
# industry = industry.rename(columns={
#     "Symbol": "symbol",
#     "Industry": "nse_industry",
#     "Industry Group": "nse_industry_group",
#     "Sub-Industry": "nse_subgroup",
#     "Basic Industry": "nse_basic_industry"
# })


# df = equity.merge(industry, on="symbol", how="left")


# # ============================================
# # YFINANCE VALIDATION
# # ============================================

# def fetch_yf_metadata(ticker):

#     try:
#         tk = yf.Ticker(ticker)

#         hist = tk.history(period="5d")

#         if hist.empty:
#             return None

#         info = tk.fast_info

#         return {
#             "is_yfinance_tradable": True,
#             "first_trade_date": tk.get_history_metadata().get("firstTradeDate"),
#             "currency": info.get("currency"),
#             "market_cap": info.get("marketCap"),
#             "avg_daily_volume": info.get("tenDayAverageVolume"),
#             "exchange_timezone": info.get("timezone")
#         }

#     except:
#         return None


# # ============================================
# # ENRICH
# # ============================================

# records = []

# for _, row in tqdm(df.iterrows(), total=len(df)):

#     meta = fetch_yf_metadata(row["yfinance_symbol"])

#     if meta:
#         row = row.to_dict()
#         row.update(meta)
#         records.append(row)


# final_df = pd.DataFrame(records)


# # ============================================
# # FLAGS
# # ============================================

# final_df["instrument_type"] = "equity"
# final_df["is_active"] = True


# # ============================================
# # SAVE
# # ============================================

# final_df.to_parquet(OUTPUT, index=False)

# print("Saved universe:", len(final_df))

import pandas as pd
import yfinance as yf
from tqdm import tqdm
from datetime import datetime
import json

# =========================================================
# CONFIGURATION
# =========================================================

EQUITY_MASTER = "universe/EQUITY_L.csv"
CLASSIFICATION = "universe/ind_nifty500list.csv"
OUTPUT = "universe/market_universe2.parquet"

# TEST MODE — set to None for full universe
TEST_SAMPLE_SIZE = None   # change to None for full build


# =========================================================
# LOAD NSE EQUITY MASTER
# =========================================================

def load_equity_master():
    df = pd.read_csv(EQUITY_MASTER)

    df = df.rename(columns={
        "SYMBOL": "symbol",
        "NAME OF COMPANY": "company_name",
        " ISIN NUMBER": "isin"
    })

    df["yfinance_symbol"] = df["symbol"] + ".NS"

    return df[["symbol", "company_name", "isin", "yfinance_symbol"]]


# =========================================================
# LOAD NSE CLASSIFICATION
# =========================================================

# def load_classification():
#     df = pd.read_csv(CLASSIFICATION)

#     df = df.rename(columns={
#         "Symbol": "symbol",
#         "Industry": "nse_industry",
#         "Industry Group": "nse_industry_group",
#         "Sub-Industry": "nse_subgroup",
#         "Basic Industry": "nse_basic_industry"
#     })

#     return df[[
#         "symbol",
#         "nse_industry",
#         "nse_industry_group",
#         "nse_subgroup",
#         "nse_basic_industry"
#     ]]

def load_classification():

    df = pd.read_csv(CLASSIFICATION)

    # normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # create mapping safely
    column_map = {}

    for col in df.columns:

        if col == "symbol":
            column_map[col] = "symbol"

        elif "industry_group" in col:
            column_map[col] = "nse_industry_group"

        elif "sub" in col and "industry" in col:
            column_map[col] = "nse_subgroup"

        elif col == "industry":
            column_map[col] = "nse_industry"

        elif "basic" in col and "industry" in col:
            column_map[col] = "nse_basic_industry"

    df = df.rename(columns=column_map)

    # ensure required columns exist
    required = [
        "symbol",
        "nse_industry",
        "nse_industry_group",
        "nse_subgroup",
        "nse_basic_industry"
    ]

    for col in required:
        if col not in df.columns:
            df[col] = None

    return df[required]


# =========================================================
# ECONOMIC EXPOSURE TAGS
# =========================================================

def generate_exposure_tags(basic_industry):

    if pd.isna(basic_industry):
        return {}

    b = basic_industry.lower()

    tags = {
        "commodity": [],
        "macro": [],
        "global": []
    }

    if "refiner" in b or "petroleum" in b:
        tags["commodity"].append("crude oil")
        tags["macro"].append("usd_inr")
        tags["global"].append("opec")

    if "steel" in b or "iron" in b:
        tags["commodity"].extend(["iron ore", "coking coal"])
        tags["global"].append("china demand")

    if "cement" in b:
        tags["commodity"].extend(["limestone", "energy"])
        tags["macro"].append("infrastructure spending")

    if "bank" in b or "financial" in b:
        tags["macro"].extend(["repo rate", "system liquidity"])

    if "software" in b or "it services" in b:
        tags["macro"].append("usd_inr")
        tags["global"].append("global tech demand")

    if "fmcg" in b or "food" in b or "consumer" in b:
        tags["macro"].append("rural demand")
        tags["macro"].append("cpi inflation")

    return tags


# =========================================================
# NEWS SEARCH TERMS
# =========================================================

def generate_news_aliases(company, symbol):
    aliases = {
        company,
        symbol,
        symbol + " share",
        symbol + " stock"
    }
    return list(aliases)


# =========================================================
# YFINANCE VALIDATION + METADATA
# =========================================================

def fetch_yf_metadata(ticker):

    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d")

        if hist.empty:
            return None

        info = tk.fast_info

        meta = tk.get_history_metadata()
        first_trade = meta.get("firstTradeDate")

        if first_trade:
            first_trade = datetime.fromtimestamp(first_trade)

        return {
            "is_yfinance_tradable": True,
            "currency": info.get("currency"),
            "market_cap": info.get("marketCap"),
            "avg_daily_volume": info.get("tenDayAverageVolume"),
            "data_start": first_trade
        }

    except:
        return None


# =========================================================
# BUILD UNIVERSE
# =========================================================

def build_universe():

    print("Loading equity master...")
    equity = load_equity_master()

    print("Loading classification...")
    industry = load_classification()

    df = equity.merge(industry, on="symbol", how="left")

    if TEST_SAMPLE_SIZE:
        print(f"TEST MODE — processing first {TEST_SAMPLE_SIZE} symbols")
        df = df.head(TEST_SAMPLE_SIZE)

    print("Validating Yahoo Finance + fetching metadata...")

    records = []

    for _, row in tqdm(df.iterrows(), total=len(df)):

        meta = fetch_yf_metadata(row["yfinance_symbol"])
        if not meta:
            continue

        row = row.to_dict()
        row.update(meta)

        # # economic exposure
        # row["exposure_tags"] = generate_exposure_tags(
        #     row.get("nse_basic_industry")
        # )

        # # news aliases
        # row["news_aliases"] = generate_news_aliases(
        #     row["company_name"],
        #     row["symbol"]
        # )

        row["exposure_tags"] = json.dumps(
            generate_exposure_tags(row.get("nse_basic_industry"))
        )

        row["news_aliases"] = json.dumps(
            generate_news_aliases(row["company_name"], row["symbol"])
        )

        row["instrument_type"] = "equity"
        row["is_active"] = True

        records.append(row)

    final_df = pd.DataFrame(records)

    print("Saving parquet...")
    final_df.to_parquet(OUTPUT, index=False)

    print("\nDONE")
    print("Final symbols:", len(final_df))
    print("Saved to:", OUTPUT)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    build_universe()