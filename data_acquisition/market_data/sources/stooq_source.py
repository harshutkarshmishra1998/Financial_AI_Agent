import pandas as pd


def fetch_stooq(ticker: str):
    try:
        url = f"https://stooq.com/q/d/l/?s={ticker.lower()}&i=d"
        df = pd.read_csv(url)

        if df.empty:
            return None

        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        return df

    except Exception:
        return None