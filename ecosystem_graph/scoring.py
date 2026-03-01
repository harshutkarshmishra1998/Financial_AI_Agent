def compute_node_importance(stat_strength, proximity, economic_weight):
    return (
        0.4 * stat_strength +
        0.3 * proximity +
        0.3 * economic_weight
    )

def edge_confidence(corr, granger_p):
    return 0.6 * abs(corr) + 0.4 * (1 - granger_p)