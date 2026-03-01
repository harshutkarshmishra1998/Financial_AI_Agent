import pandas as pd
import yfinance as yf
from fredapi import Fred
from groq import Groq
import json
import api_keys


class EntityResolver:
    """
    Uses LLM to classify economic entity into data category.
    No hardcoded mapping.
    """

    def __init__(self, groq_api_key, model="qwen-qwq-32b"):
        self.client = Groq()
        self.model = model

    def classify(self, entity_name):

        prompt = f"""
Classify the economic entity below into ONE category:

equity
index
currency
commodity
interest_rate
macro_indicator
bond_yield
unknown

Return STRICT JSON:
{{"category": "..."}}

Entity: {entity_name}
"""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return json.loads(resp.choices[0].message.content)["category"] #type: ignore
    
class SeriesLocator:

    def __init__(self, fred_api_key):
        self.fred = Fred(api_key=fred_api_key)

    # --------------------------
    # Equity / commodity / FX
    # --------------------------

    def search_yfinance(self, entity_name):

        # yfinance supports fuzzy ticker search via query endpoint
        # we approximate using ticker download attempts

        try:
            data = yf.download(entity_name, period="5y", progress=False)
            if not data.empty: #type: ignore
                return data["Close"] #type: ignore
        except:
            pass

        return None

    # --------------------------
    # FRED macro search
    # --------------------------

    def search_fred(self, entity_name):

        try:
            matches = self.fred.search(entity_name)
            if matches.empty: #type: ignore
                return None

            # choose most popular series automatically
            series_id = matches.sort_values( #type: ignore
                "popularity", ascending=False
            ).iloc[0]["id"]

            data = self.fred.get_series(series_id)
            return data

        except:
            return None
        
class SeriesNormalizer:

    def align(self, series):

        s = pd.Series(series).dropna()

        # convert to daily index
        if not isinstance(s.index, pd.DatetimeIndex):
            s.index = pd.to_datetime(s.index)

        # resample to daily forward fill
        s = s.resample("D").ffill()

        return s
    
class TimeSeriesProvider:

    def __init__(self):
        self.resolver = EntityResolver()
        self.locator = SeriesLocator()
        self.normalizer = SeriesNormalizer()

        self.cache = {}

    def get_series(self, entity_name):

        if entity_name in self.cache:
            return self.cache[entity_name]

        category = self.resolver.classify(entity_name)

        series = None

        # try market data first
        if category in ["equity", "commodity", "currency", "index"]:
            series = self.locator.search_yfinance(entity_name)

        # try macro database
        if series is None and category in [
            "macro_indicator",
            "interest_rate",
            "bond_yield"
        ]:
            series = self.locator.search_fred(entity_name)

        # fallback — try both
        if series is None:
            series = self.locator.search_yfinance(entity_name)
        if series is None:
            series = self.locator.search_fred(entity_name)

        if series is None:
            return None

        series = self.normalizer.align(series)

        self.cache[entity_name] = series
        return series