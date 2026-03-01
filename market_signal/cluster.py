# signal/cluster.py

import pandas as pd
from .config import CLUSTER_GAP_DAYS


def cluster_events(df):

    df = df[df["is_anomaly"]].copy()
    df = df.sort_index()

    clusters = []
    current_cluster = [df.index[0]]

    for i in range(1, len(df)):
        delta = (df.index[i] - df.index[i-1]).days

        if delta <= CLUSTER_GAP_DAYS:
            current_cluster.append(df.index[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [df.index[i]]

    clusters.append(current_cluster)

    return clusters