import pandas as pd


class MarketUniverse:

    def __init__(self, parquet_path: str):
        self.df = pd.read_parquet(parquet_path)
        self.df["symbol"] = self.df["symbol"].str.upper()

    def validate_symbol(self, symbol: str):
        if symbol.upper() not in self.df["symbol"].values:
            raise ValueError(f"Symbol not in market universe: {symbol}")

    def get_company_info(self, symbol: str):
        row = self.df[self.df["symbol"] == symbol.upper()]
        if row.empty:
            raise ValueError("Symbol not found")
        return row.iloc[0].to_dict()

    def get_sector_peers(self, sector: str, exclude_symbol: str, limit=5):
        peers = self.df[self.df["sector"] == sector]
        peers = peers[peers["symbol"] != exclude_symbol]
        return peers["symbol"].head(limit).tolist()