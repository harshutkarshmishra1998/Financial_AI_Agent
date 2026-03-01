import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests


class StatisticalValidator:

    def correlation(self, x, y):
        return np.corrcoef(x, y)[0, 1]

    def find_best_lag(self, x, y, max_lag=30):
        best_lag = 0
        best_corr = 0

        for lag in range(1, max_lag):
            corr = np.corrcoef(x[:-lag], y[lag:])[0, 1]
            if abs(corr) > abs(best_corr):
                best_corr = corr
                best_lag = lag

        return best_lag, best_corr

    def granger(self, x, y, max_lag=10):
        df = pd.DataFrame({"x": x, "y": y})
        result = grangercausalitytests(df[["y", "x"]], max_lag, verbose=False)

        best_p = min(result[i+1][0]['ssr_ftest'][1] for i in range(max_lag))
        return best_p

    def validate(self, x, y):
        lag, corr = self.find_best_lag(x, y)
        p = self.granger(x, y)

        accepted = abs(corr) > 0.3 and p < 0.05

        return {
            "accepted": accepted,
            "correlation": corr,
            "lag": lag,
            "granger_p": p
        }