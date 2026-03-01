# ecosystem_graph/core/propagation.py

from ecosystem_graph.data.macro_nodes import (
    INDIA_MACRO,
    GLOBAL_MACRO,
    POLICY_NODES,
    REL_TYPES
)


class PropagationEngine:

    def __init__(self, graph_engine):
        self.g = graph_engine

    # -----------------------------------------------------
    # Layer 1 — Industry Drivers
    # -----------------------------------------------------

    def inject_industry_profile(self, profile):

        for category, nodes in profile.items():
            for n in nodes:
                self.g.add_dependency(
                    n,
                    category.lower(),
                    REL_TYPES.get(category.upper(), "influenced_by")
                )

    # -----------------------------------------------------
    # Layer 2 — Macro Propagation
    # -----------------------------------------------------

    def propagate_to_macro(self):

        for node in list(self.g.graph.nodes):

            if node in INDIA_MACRO:
                # Capital flow transmission
                self.g.add_transmission(
                    node,
                    "FII Flow",
                    "macro",
                    "transmits_to"
                )
                self.g.add_transmission(
                    node,
                    "DII Flow",
                    "macro",
                    "transmits_to"
                )

            if node in GLOBAL_MACRO:
                # Dollar transmission
                self.g.add_transmission(
                    node,
                    "Dollar Index",
                    "global",
                    "transmits_to"
                )

    # -----------------------------------------------------
    # Layer 3 — Policy Propagation
    # -----------------------------------------------------

    def propagate_policy(self):

        for node in list(self.g.graph.nodes):

            if node in POLICY_NODES:
                self.g.add_transmission(
                    node,
                    "Union Budget",
                    "policy",
                    "influences"
                )

    # -----------------------------------------------------
    # Layer 4 — Macro Interconnectivity
    # -----------------------------------------------------

    def build_macro_network(self):

        # Repo → Liquidity
        self.g.add_transmission(
            "RBI Repo Rate",
            "System Liquidity",
            "macro",
            "impacts"
        )

        # Fed → Dollar Index
        self.g.add_transmission(
            "US Fed Rate",
            "Dollar Index",
            "global",
            "impacts"
        )

        # Brent → USDINR
        self.g.add_transmission(
            "Brent Crude",
            "USD/INR",
            "macro",
            "impacts"
        )