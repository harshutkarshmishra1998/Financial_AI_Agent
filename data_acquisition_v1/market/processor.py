import numpy as np
import pandas as pd


def process_price_series(df: pd.DataFrame):
    """
    Robustly extract closing prices from yfinance output.
    Handles:
    - single ticker
    - multi ticker
    - MultiIndex columns
    - empty data
    """

    if df.empty:
        return [], [], 0.0, "no_data"

    close_col = None

    # ------------------------------
    # Case 1: MultiIndex columns
    # ------------------------------
    if isinstance(df.columns, pd.MultiIndex):

        if "Close" in df.columns.get_level_values(0):
            close_col = df["Close"]

            # if still DataFrame → select first column
            if isinstance(close_col, pd.DataFrame):
                close_col = close_col.iloc[:, 0] #type: ignore

    # ------------------------------
    # Case 2: Normal columns
    # ------------------------------
    else:
        if "Close" in df.columns:
            close_col = df["Close"]

    # ------------------------------
    # Safety fallback
    # ------------------------------
    if close_col is None:
        return [], [], 0.0, "no_close_column"

    close_series = close_col.dropna()

    if close_series.empty:
        return [], [], 0.0, "no_data"

    prices = close_series.to_list()

    returns = np.diff(prices).tolist() if len(prices) > 1 else []

    volatility = float(np.std(returns)) if returns else 0.0

    trend = "sideways"
    if len(prices) > 1:
        if prices[-1] > prices[0]:
            trend = "uptrend"
        elif prices[-1] < prices[0]:
            trend = "downtrend"

    return prices, returns, volatility, trend