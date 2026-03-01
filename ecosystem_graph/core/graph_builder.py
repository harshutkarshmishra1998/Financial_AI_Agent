import networkx as nx
import hashlib


class GraphBuilder:

    def __init__(self, symbol, sector):
        self.graph = nx.DiGraph()
        self.symbol = symbol
        self.sector = sector

        self.add_node(symbol, "company", depth=0)

    def add_node(self, name, node_type, depth):
        if name not in self.graph:
            self.graph.add_node(
                name,
                type=node_type,
                depth=depth
            )

    def add_edge(self, src, dst, relation):
        self.graph.add_edge(src, dst, relation=relation)

    def hash_graph(self):
        raw = "".join(sorted(self.graph.nodes)) + "".join(
            f"{u}->{v}" for u, v in self.graph.edges
        )
        return hashlib.sha256(raw.encode()).hexdigest()