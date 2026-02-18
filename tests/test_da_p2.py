import pandas as pd

from data_acquisition.common.normalization import DataNormalizer
from data_acquisition.common.data_quality import DataQualityEvaluator
from data_acquisition.common.source_scoring import SourceScorer


data = {
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "Open": [100, 101, 102],
    "High": [101, 102, 103],
    "Low": [99, 100, 101],
    "Close": [100.5, 101.5, 102.5]
}

df = pd.DataFrame(data)

norm = DataNormalizer.normalize_market_df(df)
quality = DataQualityEvaluator.evaluate_market(norm)
score = SourceScorer.score(quality)

print(norm.head())
print("Quality:", quality)
print("Score:", score)

quality_strict = DataQualityEvaluator.evaluate_market(norm, min_rows=5)
quality_lenient = DataQualityEvaluator.evaluate_market(norm, min_rows=2)

print("Strict:", quality_strict)
print("Lenient:", quality_lenient)