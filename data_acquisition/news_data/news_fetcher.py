from typing import Dict, List

from data_acquisition.news_data.sources.newsapi_source import fetch_newsapi
from data_acquisition.news_data.sources.gnews_source import fetch_gnews
from data_acquisition.news_data.normalizers.article_normalizer import ArticleNormalizer
from data_acquisition.news_data.selectors.news_selector import NewsSelector


class NewsDataFetcher:

    def __init__(self):
        self.selector = NewsSelector()

    def fetch(self, assets: List[str], plan) -> Dict:

        results = {}

        # ---------------------------------
        # determine time window
        # ---------------------------------
        from_date = None
        to_date = None

        if plan.event_window:
            from_date = plan.event_window.get("start")
            to_date = plan.event_window.get("end")

        # ---------------------------------
        # fetch per asset
        # ---------------------------------
        for asset in assets:

            articles = []

            # NewsAPI
            raw = fetch_newsapi(asset, from_date, to_date)
            for a in raw:
                norm = ArticleNormalizer.normalize_newsapi(a)
                articles.append(ArticleNormalizer.finalize(norm))

            # GNews
            raw = fetch_gnews(asset, from_date, to_date)
            for a in raw:
                norm = ArticleNormalizer.normalize_gnews(a)
                articles.append(ArticleNormalizer.finalize(norm))

            # select best
            selected = self.selector.select(articles)

            if selected:
                results[asset] = selected[:20]  # limit top 20

        return results