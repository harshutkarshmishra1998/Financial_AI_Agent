class ExpansionController:
    def __init__(self, max_nodes=120, max_depth=5, competitor_limit=5):
        self.max_nodes = max_nodes
        self.max_depth = max_depth
        self.competitor_limit = competitor_limit

    def allow_expansion(self, current_node_count, depth):
        return current_node_count < self.max_nodes and depth < self.max_depth

    def trim_competitors(self, competitors):
        return competitors[: self.competitor_limit]
