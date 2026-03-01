# market_signal/data.py

import yfinance as yf
import pandas as pd


def fetch_ohlcv(symbol: str, start: str, end: str) -> pd.DataFrame:

    df = yf.download(symbol, start=start, end=end, progress=False)

    if df.empty: #type: ignore
        raise ValueError(f"No data for {symbol}")

    # ---------------------------------------------
    # Flatten MultiIndex columns if present
    # ---------------------------------------------
    if isinstance(df.columns, pd.MultiIndex): #type: ignore
        df.columns = df.columns.get_level_values(0) #type: ignore

    df.columns = [c.lower() for c in df.columns] #type: ignore

    required_cols = ["open", "high", "low", "close", "volume"]

    missing = set(required_cols) - set(df.columns) #type: ignore
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required_cols] #type: ignore

    df.index.name = "date"

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.dropna()

    # ---------------------------------------------
    # Force numeric columns explicitly
    # ---------------------------------------------
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    return df