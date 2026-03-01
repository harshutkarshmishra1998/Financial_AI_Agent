from .models import GraphNode, GraphEdge


class EcosystemGraphEngine:

    def __init__(self, llm, data_provider, validator, controller):
        self.llm = llm
        self.data = data_provider
        self.validator = validator
        self.controller = controller

        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge):
        self.edges.append(edge)

    # -------------------------
    # recursive expansion
    # -------------------------

    def expand(self, node, depth=0):

        if not self.controller.allow_expansion(len(self.nodes), depth):
            return

        candidates = self.llm.propose_related_factors(node.name)

        for c in candidates:

            series_a = self.data.get_series(node.name)
            series_b = self.data.get_series(c["name"])

            if series_a is None or series_b is None:
                continue

            result = self.validator.validate(series_a, series_b)

            if not result["accepted"]:
                continue

            new_node = GraphNode(
                id=c["name"],
                name=c["name"],
                node_type=c["type"],
                economic_layer="derived"
            )

            self.add_node(new_node)

            self.add_edge(GraphEdge(
                source_node_id=new_node.id,
                target_node_id=node.id,
                relationship_type=c["relationship"],
                lag_days=result["lag"],
                correlation_strength=result["correlation"],
                causal_confidence=1 - result["granger_p"],
                evidence_type="statistical"
            ))

            self.expand(new_node, depth + 1)