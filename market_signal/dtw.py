# signal/dtw.py

import numpy as np
from fastdtw import fastdtw #type: ignore
from scipy.spatial.distance import euclidean
from .config import DTW_WINDOW


def compute_dtw_similarity(series1, series2):

    distance, _ = fastdtw(series1, series2, dist=euclidean)
    return distance


def rolling_dtw(df):

    closes = df["close"].values
    similarities = []

    for i in range(DTW_WINDOW, len(closes)):
        window1 = closes[i-DTW_WINDOW:i]
        window2 = closes[i-DTW_WINDOW-1:i-1]

        dist = compute_dtw_similarity(window1, window2)
        similarities.append(dist)

    return np.array(similarities)