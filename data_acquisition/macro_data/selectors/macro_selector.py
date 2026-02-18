class MacroSelector:
    """
    Determines which macro indicators to fetch.
    """

    DEFAULT_SERIES = {
        "US": {
            "CPI": "CPIAUCSL",      # inflation
            "FED_RATE": "FEDFUNDS", # interest rate
            "GDP": "GDP",
            "UNEMP": "UNRATE"
        }
    }

    def select_series(self, plan):

        # future: detect country from assets
        country = "US"

        return self.DEFAULT_SERIES[country]