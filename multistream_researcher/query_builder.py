def build_queries(anomaly_event, graph_nodes, window_days=7):
    date = anomaly_event["timestamp"]
    symbol = anomaly_event.get("symbol", "")

    base_terms = set(graph_nodes)

    templates = [
        "{term} news {date}",
        "{term} India {date}",
        "{term} policy announcement {date}",
        "{term} macro impact {date}"
    ]

    queries = []
    for term in base_terms:
        for t in templates:
            queries.append(t.format(term=term, date=date[:7]))

    if symbol:
        queries.append(f"{symbol} stock movement reason {date[:7]}")

    return list(set(queries))
