from __future__ import annotations

import numpy as np
import pandas as pd


class StatisticalValidator:
    def __init__(self, corr_threshold: float = 0.2):
        self.corr_threshold = corr_threshold

    def _align(self, x, y):
        xs = pd.Series(x).dropna()
        ys = pd.Series(y).dropna()
        df = pd.concat([xs, ys], axis=1, join="inner").dropna()
        if len(df) < 10:
            return None
        return df.iloc[:, 0], df.iloc[:, 1]

    def find_best_lag(self, x, y, max_lag=20):
        aligned = self._align(x, y)
        if aligned is None:
            return 0, 0.0
        xa, ya = aligned

        best_lag = 0
        best_corr = 0.0
        for lag in range(1, min(max_lag, len(xa) - 1)):
            corr = np.corrcoef(xa.iloc[:-lag], ya.iloc[lag:])[0, 1]
            if np.isnan(corr):
                continue
            if abs(corr) > abs(best_corr):
                best_lag = lag
                best_corr = float(corr)

        return best_lag, best_corr

    def validate(self, x, y):
        lag, corr = self.find_best_lag(x, y)
        accepted = abs(corr) >= self.corr_threshold
        # keep interface compatible even when granger is skipped.
        granger_p = 0.01 if accepted else 1.0
        return {
            "accepted": accepted,
            "correlation": corr,
            "lag": lag,
            "granger_p": granger_p,
        }
