from data.ontology import (
    SECTOR_DEPENDENCIES,
    INDIA_MACRO,
    GLOBAL_MACRO,
    POLICY_NODES,
    REL_TYPES
)


class GraphExpander:

    def __init__(self, builder, universe, llm=None):
        self.b = builder
        self.universe = universe
        self.llm = llm

    # ---------- Supply Chain ----------
    def expand_supply(self):
        deps = SECTOR_DEPENDENCIES.get(self.b.sector, [])
        for d in deps:
            self.b.add_node(d, "commodity", 1)
            self.b.add_edge(self.b.symbol, d, REL_TYPES["INPUT"])

    # ---------- Competitors ----------
    def expand_competitors(self):
        peers = self.universe.get_sector_peers(
            self.b.sector,
            self.b.symbol
        )
        for p in peers:
            self.b.add_node(p, "company", 1)
            self.b.add_edge(self.b.symbol, p, REL_TYPES["COMPETITOR"])

    # ---------- Macro ----------
    def inject_macro(self):
        for m in INDIA_MACRO + GLOBAL_MACRO:
            self.b.add_node(m, "macro", 2)
            self.b.add_edge(self.b.symbol, m, REL_TYPES["MACRO"])

    # ---------- Policy ----------
    def inject_policy(self):
        for p in POLICY_NODES:
            self.b.add_node(p, "policy", 2)
            self.b.add_edge(self.b.symbol, p, REL_TYPES["POLICY"])

    # ---------- LLM ----------
    def expand_llm(self):
        if not self.llm:
            return
        res = self.llm.extract_candidates(
            self.b.symbol,
            self.b.sector,
            list(self.b.graph.nodes)
        )
        for n in res["nodes"]:
            self.b.add_node(n["name"], n["type"], 2)
        for e in res["edges"]:
            self.b.add_edge(e["source"], e["target"], e["relation"])