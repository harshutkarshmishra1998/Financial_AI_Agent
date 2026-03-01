# ecosystem_graph/core/graph_validator.py

import pandas as pd


class GraphValidator:

    def __init__(self, builder):
        self.b = builder

    def ensure_non_empty(self):
        if len(self.b.graph.nodes) <= 1:
            raise ValueError("Graph expansion failed")

    def to_frames(self):

        nodes = [
            {"node": n, **d}
            for n, d in self.b.graph.nodes(data=True)
        ]

        edges = [
            {"source": u, "target": v, **d}
            for u, v, d in self.b.graph.edges(data=True)
        ]

        return pd.DataFrame(nodes), pd.DataFrame(edges)