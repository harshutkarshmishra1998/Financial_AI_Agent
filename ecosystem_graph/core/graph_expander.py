# ecosystem_graph/core/graph_expander.py

from ecosystem_graph.data.ontology import INDUSTRY_DEPENDENCY_PROFILE


class GraphExpander:

    def __init__(self, builder):
        self.b = builder

    def expand_from_industry(self):

        profile = INDUSTRY_DEPENDENCY_PROFILE.get(self.b.industry, {})

        for category, factors in profile.items():
            for factor in factors:
                self.b.add_node(factor, category)
                self.b.add_edge(self.b.symbol, factor, "influenced_by")