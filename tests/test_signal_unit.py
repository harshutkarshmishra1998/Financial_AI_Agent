from market_signal.features import engineer_features
import pandas as pd
import numpy as np


def test_feature_engineering():

    df = pd.DataFrame({
        "open": np.random.rand(100),
        "high": np.random.rand(100),
        "low": np.random.rand(100),
        "close": np.random.rand(100),
        "volume": np.random.randint(1000, 5000, 100),
    })

    df.index = pd.date_range("2020-01-01", periods=100)

    result = engineer_features(df)

    # assert "z_score" in result.columns
    # assert not result.isna().any().any()

    print(result)

if __name__ == "__main__":
    test_feature_engineering()