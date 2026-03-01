# ecosystem_graph/core/graph_engine.py

import networkx as nx
import hashlib


class EcosystemGraphEngine:

    def __init__(self, root_ticker, industry):

        self.root = root_ticker
        self.industry = industry
        self.graph = nx.DiGraph()

        self._add_node(self.root, "company")

    # ------------------------
    # Basic Graph Ops
    # ------------------------

    def _add_node(self, name, node_type):
        if name not in self.graph:
            self.graph.add_node(name, type=node_type)

    def _add_edge(self, src, dst, relation):
        self.graph.add_edge(src, dst, relation=relation)

    # ------------------------
    # Public API
    # ------------------------

    def add_dependency(self, node, node_type, relation):
        self._add_node(node, node_type)
        self._add_edge(self.root, node, relation)

    def add_transmission(self, src, dst, dst_type, relation):
        self._add_node(dst, dst_type)
        self._add_edge(src, dst, relation)

    def get_hash(self):
        raw = "".join(sorted(self.graph.nodes))
        return hashlib.sha256(raw.encode()).hexdigest()

    def export(self):
        nodes = [
            {"node": n, **d} #type: ignore
            for n, d in self.graph.nodes(data=True)
        ]

        edges = [
            {"source": u, "target": v, **d} #type: ignore
            for u, v, d in self.graph.edges(data=True) #type: ignore
        ]

        return nodes, edges