# ecosystem_graph/core/graph_builder.py

import networkx as nx
import hashlib


class GraphBuilder:

    def __init__(self, symbol, industry):
        self.symbol = symbol
        self.industry = industry
        self.graph = nx.DiGraph()

        self.add_node(symbol, "company")

    def add_node(self, name, node_type):
        if name not in self.graph:
            self.graph.add_node(name, type=node_type)

    def add_edge(self, src, dst, relation):
        self.graph.add_edge(src, dst, relation=relation)

    def hash_graph(self):
        raw = "".join(sorted(self.graph.nodes))
        return hashlib.sha256(raw.encode()).hexdigest()