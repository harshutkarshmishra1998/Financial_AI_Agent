# from typing import Dict, List

# from data_acquisition.market_data.selectors.market_source_selector import MarketSourceSelector


# class MarketDataFetcher:

#     def __init__(self):
#         self.selector = MarketSourceSelector()

#     def fetch(self, assets: List[str], plan) -> Dict:

#         results = {}

#         for ticker in assets:

#             source, df = self.selector.fetch_best(
#                 ticker=ticker,
#                 time_profile=plan.time_profile,
#                 min_rows=plan.min_required_rows
#             )

#             if df is None:
#                 continue

#             results[ticker] = {
#                 "source": source,
#                 "rows": len(df),
#                 "data": df
#             }

#         return results

from typing import Dict, List

from data_acquisition.market_data.selectors.market_source_selector import MarketSourceSelector
from data_acquisition.pipeline.adaptive_executor import AdaptiveMarketExecutor


class MarketDataFetcher:

    def __init__(self):
        self.selector = MarketSourceSelector()
        self.executor = AdaptiveMarketExecutor(self.selector)

    def fetch(self, assets: List[str], plan) -> Dict:

        results = {}

        for ticker in assets:

            source, df, attempts = self.executor.fetch_with_retry(
                ticker,
                plan
            )

            if df is None:
                continue

            results[ticker] = {
                "source": source,
                "rows": len(df),
                "attempts": attempts,
                "data": df
            }

        return results