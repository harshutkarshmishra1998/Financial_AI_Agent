import pandas as pd


class GraphValidator:

    def __init__(self, builder):
        self.b = builder

    def ensure_macro_presence(self):
        macros = [n for n, d in self.b.graph.nodes(data=True) if d["type"] == "macro"]
        if not macros:
            raise ValueError("Macro layer missing")

    def to_dataframes(self):
        nodes = []
        for n, d in self.b.graph.nodes(data=True):
            nodes.append({"node": n, **d})

        edges = []
        for u, v, d in self.b.graph.edges(data=True):
            edges.append({"source": u, "target": v, **d})

        return pd.DataFrame(nodes), pd.DataFrame(edges)