from data_acquisition.common.normalization import DataNormalizer
from data_acquisition.common.data_quality import DataQualityEvaluator
from data_acquisition.common.source_scoring import SourceScorer

from data_acquisition.market_data.sources.yfinance_source import fetch_yfinance
from data_acquisition.market_data.sources.alpha_vantage_source import fetch_alpha_vantage
from data_acquisition.market_data.sources.stooq_source import fetch_stooq


class MarketSourceSelector:

    def fetch_best(self, ticker, time_profile, min_rows):

        candidates = []

        # yfinance
        if "period" in time_profile:
            raw = fetch_yfinance(
                ticker,
                time_profile["period"],
                time_profile["interval"]
            )
            self._evaluate("yfinance", raw, min_rows, candidates)

        # alpha vantage
        raw = fetch_alpha_vantage(ticker)
        self._evaluate("alpha_vantage", raw, min_rows, candidates)

        # stooq
        raw = fetch_stooq(ticker)
        self._evaluate("stooq", raw, min_rows, candidates)

        if not candidates:
            return None, None

        best = max(candidates, key=lambda x: x["score"])
        return best["source"], best["data"]

    def _evaluate(self, name, raw, min_rows, bucket):
        if raw is None:
            return

        norm = DataNormalizer.normalize_market_df(raw)
        quality = DataQualityEvaluator.evaluate_market(norm, min_rows=min_rows)
        score = SourceScorer.score(quality)

        if quality["valid"]:
            bucket.append({
                "source": name,
                "data": norm,
                "score": score
            })