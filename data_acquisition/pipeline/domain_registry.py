from data_acquisition.market_data.market_fetcher import MarketDataFetcher
from data_acquisition.news_data.news_fetcher import NewsDataFetcher
from data_acquisition.macro_data.macro_fetcher import MacroDataFetcher

class DomainRegistry:
    """
    Central mapping of domain → fetcher.
    """

    REGISTRY = {
        "market": MarketDataFetcher,
        "news": NewsDataFetcher,
        "macro": MacroDataFetcher
    }

    @classmethod
    def get_fetcher(cls, domain: str):
        fetcher_class = cls.REGISTRY.get(domain)
        if not fetcher_class:
            return None
        return fetcher_class()