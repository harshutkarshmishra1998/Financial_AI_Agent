class ExpansionController:

    def __init__(self, max_nodes=60, max_depth=4):
        self.max_nodes = max_nodes
        self.max_depth = max_depth

    def allow_expansion(self, current_node_count, depth):
        if current_node_count >= self.max_nodes:
            return False
        if depth >= self.max_depth:
            return False
        return True