import json
from ecosystem_graph.data.company_dependence_rules import ALLOWED_DEPENDENCIES


class CompanyDependencyExpander:
    """
    Hybrid LLM + ontology validated supplier / customer network.
    """

    def __init__(
        self,
        graph_engine,
        llm,
        max_partners_per_type=5
    ):
        self.graph = graph_engine
        self.llm = llm
        self.max_partners = max_partners_per_type

    # --------------------------------------------------
    # PUBLIC ENTRY
    # --------------------------------------------------

    def expand(self, company_ticker, sector):

        if sector not in ALLOWED_DEPENDENCIES:
            return

        allowed = ALLOWED_DEPENDENCIES[sector]

        raw = self._llm_generate(company_ticker, sector)

        validated = self._validate(raw, allowed)

        self._insert(company_ticker, validated)

    # --------------------------------------------------
    # LLM GENERATION
    # --------------------------------------------------

    def _llm_generate(self, company, sector):

        prompt = f"""
You are building an industrial economic dependency network.

Company: {company}
Sector: {sector}

Generate realistic business dependencies.

Return JSON:

{{
 "suppliers": ["company or entity names"],
 "customers": ["company or entity names"],
 "strategic": ["partner names"]
}}

Rules:
- real company types or institutions
- no explanation
- no markdown
- JSON only
- max 5 each
"""

        response = self.llm.invoke(prompt)

        return self._safe_json(response)

    # --------------------------------------------------
    # ONTOLOGY VALIDATION
    # --------------------------------------------------

    def _validate(self, raw, allowed):

        clean = {
            "suppliers": [],
            "customers": [],
            "strategic": []
        }

        for k in clean.keys():

            if k not in raw:
                continue

            allowed_types = allowed.get(k, [])

            for item in raw[k][: self.max_partners]:

                name = str(item).strip()

                if not name:
                    continue

                # basic semantic validation
                if self._matches_allowed_category(name, allowed_types):
                    clean[k].append(name)

        return clean

    def _matches_allowed_category(self, name, allowed_types):
        """
        Lightweight semantic filter.
        Can be upgraded to embedding similarity later.
        """

        lowered = name.lower()

        for t in allowed_types:
            if any(word in lowered for word in t.lower().split()):
                return True

        return False

    # --------------------------------------------------
    # GRAPH INSERTION
    # --------------------------------------------------

    def _insert(self, company, deps):

        for supplier in deps["suppliers"]:

            if not self.graph.has_node(supplier):
                self.graph._add_node(supplier, node_type="supplier")

            self.graph._add_edge(supplier, company, "supplies_to")

        for customer in deps["customers"]:

            if not self.graph.has_node(customer):
                self.graph._add_node(customer, node_type="customer")

            self.graph._add_edge(company, customer, "sells_to")

        for partner in deps["strategic"]:

            if not self.graph.has_node(partner):
                self.graph._add_node(partner, node_type="strategic")

            self.graph._add_edge(company, partner, "strategic_dependency")

    # --------------------------------------------------
    # SAFE JSON PARSE
    # --------------------------------------------------

    def _safe_json(self, text):

        if isinstance(text, dict):
            return text

        start = text.find("{")
        end = text.rfind("}") + 1

        return json.loads(text[start:end])