
def score(meta, similarity, event_date, graph_nodes):

    graph_score = len(set(meta.get("matched_nodes", []))) / max(len(graph_nodes),1)

    return (
        0.6 * similarity +
        0.25 * graph_score +
        0.15 * meta.get("credibility", 0.5)
    )
