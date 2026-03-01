import pandas as pd


class MarketUniverse:

    def __init__(self, path):
        self.df = pd.read_parquet(path)

        # normalize for fast lookup
        self.df["symbol_upper"] = self.df["symbol"].str.upper()
        self.df["yf_upper"] = self.df["yfinance_symbol"].str.upper()

    # -------------------------------------------------
    # UNIVERSAL SYMBOL RESOLVER
    # -------------------------------------------------
    def get_company(self, query):

        q = query.upper()

        # 1️⃣ direct NSE symbol match
        match = self.df[self.df.symbol_upper == q]
        if not match.empty:
            return match.iloc[0].to_dict()

        # 2️⃣ direct yfinance ticker match
        match = self.df[self.df.yf_upper == q]
        if not match.empty:
            return match.iloc[0].to_dict()

        # 3️⃣ user typed TCS but stored TCS.NS
        if not q.endswith(".NS"):
            match = self.df[self.df.yf_upper == q + ".NS"]
            if not match.empty:
                return match.iloc[0].to_dict()

        raise ValueError(f"Symbol not found: {query}")