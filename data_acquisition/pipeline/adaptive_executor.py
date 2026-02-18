from typing import Tuple
from data_acquisition.pipeline.retry_manager import RetryManager


class AdaptiveMarketExecutor:
    """
    Executes progressive fetch attempts until data sufficiency achieved.
    """

    def __init__(self, selector):
        self.selector = selector
        self.retry_manager = RetryManager()

    def fetch_with_retry(self, ticker: str, plan) -> Tuple[str, object, int]:

        profiles = self.retry_manager.generate_attempt_profiles(
            plan.time_profile,
            plan.retry_policy["max_attempts"]
        )

        attempt = 0

        for profile in profiles:
            attempt += 1

            source, df = self.selector.fetch_best(
                ticker=ticker,
                time_profile=profile,
                min_rows=plan.min_required_rows
            )

            if df is not None:
                return source, df, attempt

        return None, None, attempt