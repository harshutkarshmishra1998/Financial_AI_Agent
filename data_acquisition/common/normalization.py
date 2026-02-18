# import pandas as pd
# from typing import Dict


# class DataNormalizer:
#     """
#     Converts raw provider data into canonical schema.
#     """

#     STANDARD_COLUMN_MAP = {
#         "Date": "timestamp",
#         "Datetime": "timestamp",
#         "time": "timestamp",
#         "Open": "open",
#         "High": "high",
#         "Low": "low",
#         "Close": "close",
#         "Adj Close": "adj_close",
#         "Volume": "volume"
#     }

#     @staticmethod
#     def normalize_market_df(df: pd.DataFrame) -> pd.DataFrame:
#         """
#         Normalize market OHLC dataframe to canonical schema.
#         """

#         if df is None or df.empty:
#             return df

#         df = df.copy()

#         # rename columns
#         df.rename(columns=DataNormalizer.STANDARD_COLUMN_MAP, inplace=True)

#         # ensure timestamp column
#         if "timestamp" not in df.columns:
#             df["timestamp"] = df.index

#         # datetime conversion
#         df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

#         # sort chronologically
#         df = df.sort_values("timestamp")

#         # drop duplicates
#         df = df.drop_duplicates(subset=["timestamp"])

#         # numeric coercion
#         numeric_cols = ["open", "high", "low", "close", "volume", "adj_close"]

#         for col in numeric_cols:
#             if col in df.columns:
#                 df[col] = pd.to_numeric(df[col], errors="coerce")

#         # reset index
#         df = df.reset_index(drop=True)

#         return df

import pandas as pd


class DataNormalizer:
    """
    Fully robust market dataframe normalization.

    Handles:
    - index timestamps
    - unnamed index
    - multi-index index
    - multi-index columns (yfinance grouped output)
    - column tuples
    - provider inconsistencies
    """

    STANDARD_COLUMN_MAP = {
        "date": "timestamp",
        "datetime": "timestamp",
        "time": "timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adj close": "adj_close",
        "adj_close": "adj_close",
        "volume": "volume"
    }

    @staticmethod
    def normalize_market_df(df: pd.DataFrame) -> pd.DataFrame:

        if df is None or df.empty:
            return df

        df = df.copy()

        # -------------------------------------------------
        # STEP 1 — flatten multi-index columns
        # -------------------------------------------------
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                "_".join([str(x) for x in col if x]).strip()
                for col in df.columns
            ]

        # -------------------------------------------------
        # STEP 2 — force index into column
        # -------------------------------------------------
        if not isinstance(df.index, pd.RangeIndex):
            df = df.reset_index()

        # -------------------------------------------------
        # STEP 3 — normalize column names (lowercase)
        # -------------------------------------------------
        df.columns = [str(c).strip().lower() for c in df.columns]

        # -------------------------------------------------
        # STEP 4 — map columns to canonical names
        # -------------------------------------------------
        rename_map = {}
        for col in df.columns:
            for key, target in DataNormalizer.STANDARD_COLUMN_MAP.items():
                if key in col:
                    rename_map[col] = target
        df.rename(columns=rename_map, inplace=True)

        # -------------------------------------------------
        # STEP 5 — ensure timestamp column exists
        # -------------------------------------------------
        if "timestamp" not in df.columns:
            for fallback in ["index", "level_0"]:
                if fallback in df.columns:
                    df.rename(columns={fallback: "timestamp"}, inplace=True)
                    break

        if "timestamp" not in df.columns:
            raise ValueError(
                f"Timestamp column could not be determined. Columns: {list(df.columns)}"
            )

        # -------------------------------------------------
        # STEP 6 — convert timestamp
        # -------------------------------------------------
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # -------------------------------------------------
        # STEP 7 — sort + deduplicate
        # -------------------------------------------------
        df = df.sort_values("timestamp")
        df = df.drop_duplicates(subset=["timestamp"])

        # -------------------------------------------------
        # STEP 8 — numeric coercion
        # -------------------------------------------------
        numeric_cols = ["open", "high", "low", "close", "volume", "adj_close"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # -------------------------------------------------
        # STEP 9 — reset index
        # -------------------------------------------------
        df = df.reset_index(drop=True)

        return df