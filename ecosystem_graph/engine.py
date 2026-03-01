from __future__ import annotations

from typing import Dict, Iterable, Optional

from .config import DEFAULT_COMPETITOR_LIMIT, GLOBAL_DRIVERS, INDIAN_STRUCTURAL_DRIVERS
from .models import GraphBundle, GraphEdge, GraphNode


class EcosystemGraphEngine:
    def __init__(self, llm, data_provider, validator, controller):
        self.llm = llm
        self.data = data_provider
        self.validator = validator
        self.controller = controller
        if not hasattr(self.controller, "competitor_limit"):
            self.controller.competitor_limit = DEFAULT_COMPETITOR_LIMIT

        self.nodes: Dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode):
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    @staticmethod
    def _node_id(node_type: str, name: str) -> str:
        return f"{node_type}:{name.lower().strip()}"

    def _upsert_node(self, name: str, node_type: str, layer: str, source: str = "deterministic") -> GraphNode:
        node_id = self._node_id(node_type, name)
        node = self.nodes.get(node_id)
        if node is None:
            node = GraphNode(id=node_id, name=name, node_type=node_type, economic_layer=layer, source=source)
            self.add_node(node)
        return node

    def _connect(self, src: GraphNode, tgt: GraphNode, rel: str, evidence="structural", stats: Optional[Dict] = None):
        edge = GraphEdge(
            source_node_id=src.id,
            target_node_id=tgt.id,
            relationship_type=rel,
            evidence_type=evidence,
            lag_days=(stats or {}).get("lag"),
            correlation_strength=(stats or {}).get("correlation"),
            causal_confidence=1 - (stats or {}).get("granger_p", 1),
        )
        self.add_edge(edge)

    def _attach_influencers(self, parent: GraphNode, names: Iterable[str], layer: str):
        for name in names:
            inf = self._upsert_node(name, "macro", layer)
            self._connect(inf, parent, "influenced_by")

    def _attach_macro_baseline(self, company: GraphNode):
        for driver_group in INDIAN_STRUCTURAL_DRIVERS.values():
            for driver in driver_group:
                macro = self._upsert_node(driver, "macro", "domestic_macro")
                self._connect(macro, company, "influenced_by")

        for driver in GLOBAL_DRIVERS:
            macro = self._upsert_node(driver, "macro", "global_macro")
            self._connect(macro, company, "influenced_by")

    def _build_deterministic_structure(self, symbol: str, company: GraphNode, depth: int = 0):
        profile = self.data.get_company_profile(symbol)

        sector_name = profile.get("sector")
        if sector_name:
            sector = self._upsert_node(sector_name, "sector", "core")
            self._connect(company, sector, "classified_in")

        for inp in self.data.iter_company_inputs(symbol):
            input_name = inp["name"]
            input_node = self._upsert_node(input_name, "input", "supply")
            self._connect(company, input_node, "depends_on")

            deps = self.data.get_input_dependencies(symbol, input_name)
            for prod in deps.get("producers", []):
                prod_node = self._upsert_node(prod, "producer", "supply")
                self._connect(input_node, prod_node, "produced_by")

            for comp in deps.get("competing_materials", []):
                comp_node = self._upsert_node(comp, "competing_material", "competition")
                self._connect(comp_node, input_node, "competes_with")

            self._attach_influencers(input_node, deps.get("influenced_by", []), "global_macro")

        for out in self.data.iter_company_outputs(symbol):
            output_name = out["name"]
            out_node = self._upsert_node(output_name, "output", "demand")
            self._connect(company, out_node, "produces")

            deps = self.data.get_output_dependencies(symbol, output_name)
            for sector in deps.get("consumer_sectors", []):
                c_node = self._upsert_node(sector, "consumer_sector", "demand")
                self._connect(out_node, c_node, "consumed_by")

            for comp_prod in deps.get("competing_products", []):
                cp_node = self._upsert_node(comp_prod, "competing_product", "competition")
                self._connect(cp_node, out_node, "competes_with")

            self._attach_influencers(out_node, deps.get("influenced_by", []), "domestic_macro")

        for competitor in self.controller.trim_competitors(self.data.iter_competitors(symbol)):
            comp_node = self._upsert_node(competitor, "company", "competition")
            self._connect(comp_node, company, "direct_competitor")
            if self.controller.allow_expansion(len(self.nodes), depth + 1) and self.data.get_company_profile(competitor):
                self._build_deterministic_structure(competitor, comp_node, depth=depth + 1)

    def _validate_structural_edges(self):
        for edge in self.edges:
            src = self.nodes[edge.source_node_id]
            tgt = self.nodes[edge.target_node_id]
            xs = self.data.get_series(src.name)
            ys = self.data.get_series(tgt.name)
            if xs is None or ys is None:
                continue
            result = self.validator.validate(xs, ys)
            edge.lag_days = result["lag"]
            edge.correlation_strength = result["correlation"]
            edge.causal_confidence = 1 - result["granger_p"]
            edge.evidence_type = "hybrid" if result["accepted"] else edge.evidence_type

    def _expand_with_llm_candidates(self, company: GraphNode):
        for cand in self.llm.propose_related_factors(company.name, context={"node_count": len(self.nodes)}):
            if not self.controller.allow_expansion(len(self.nodes), depth=1):
                break
            name = cand.get("name")
            if not name:
                continue
            node = self._upsert_node(name, cand.get("type", "factor"), "derived", source="llm")
            xs = self.data.get_series(node.name)
            ys = self.data.get_series(company.name)
            if xs is None or ys is None:
                continue
            stat = self.validator.validate(xs, ys)
            if not stat["accepted"]:
                continue
            self._connect(node, company, cand.get("relationship", "influenced_by"), evidence="statistical", stats=stat)

    def build(self, symbol: str) -> GraphBundle:
        company_name = self.data.get_company_profile(symbol).get("company_name", symbol)
        company = self._upsert_node(company_name, "company", "core")

        self._build_deterministic_structure(symbol, company, depth=0)
        self._attach_macro_baseline(company)
        self._expand_with_llm_candidates(company)
        self._validate_structural_edges()

        return GraphBundle(nodes=list(self.nodes.values()), edges=self.edges)
