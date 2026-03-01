# signal/features.py

import numpy as np
import pandas as pd
from .config import FEATURE_WINDOW


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["rolling_mean"] = df["log_return"].rolling(FEATURE_WINDOW).mean()
    df["rolling_std"] = df["log_return"].rolling(FEATURE_WINDOW).std()

    df["z_score"] = (
        (df["log_return"] - df["rolling_mean"]) /
        df["rolling_std"]
    )

    df["volume_z"] = (
        (df["volume"] - df["volume"].rolling(FEATURE_WINDOW).mean()) /
        df["volume"].rolling(FEATURE_WINDOW).std()
    )

    df = df.dropna()

    return df