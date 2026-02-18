import yfinance as yf #type: ignore


def fetch_yfinance(ticker: str, period: str, interval: str):
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False
        )
        return df
    except Exception:
        return None