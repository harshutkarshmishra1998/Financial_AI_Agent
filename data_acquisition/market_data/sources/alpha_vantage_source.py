import os
import requests
import pandas as pd


def fetch_alpha_vantage(ticker: str):
    key = os.getenv("ALPHA_VANTAGE")
    if not key:
        return None

    try:
        url = (
            "https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_DAILY"
            f"&symbol={ticker}"
            f"&outputsize=compact"
            f"&apikey={key}"
        )

        data = requests.get(url, timeout=20).json()

        if "Time Series (Daily)" not in data:
            return None

        df = (
            pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            .rename(columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            })
        )

        df.index = pd.to_datetime(df.index)
        df = df.astype(float).sort_index()
        return df

    except Exception:
        return None