import json
from collections import deque


class SupplyDemandExpander:
    """
    Graph-safe recursive expansion of supply and demand drivers.

    Guarantees:
    - depth control
    - no cycles
    - no duplicates
    - bounded branching
    """

    def __init__(
        self,
        graph_engine,
        llm,
        max_depth=3,
        max_children_per_node=4
    ):
        self.graph = graph_engine
        self.llm = llm
        self.max_depth = max_depth
        self.max_children = max_children_per_node

        # global visited registry
        self.visited = set()

    # PUBLIC ENTRYPOINT
    def expand(self, root_node, sector):
        """
        Expand supply-demand structure starting from root.
        """

        queue = deque()
        queue.append((root_node, 0))
        self.visited.add(root_node)

        while queue:
            node, depth = queue.popleft()

            if depth >= self.max_depth:
                continue

            children = self._generate_children(node, sector)

            for child_name, relation_type in children:

                if not self._is_valid_new_node(node, child_name):
                    continue

                # create node
                self.graph._add_node(
                    child_name,
                    node_type=relation_type
                )

                # create directional edge
                self.graph._add_edge(
                    src=node,
                    dst=child_name,
                    relation=relation_type
                )

                self.visited.add(child_name)
                queue.append((child_name, depth + 1))

    # LLM GENERATION
    def _generate_children(self, node_name, sector):
        """
        Ask LLM for supply and demand drivers.
        Returns list of tuples: (node_name, relation_type)
        """

        prompt = f"""
You are an economic systems modeler building a causal graph.

STRICT RULES:
- Return ONLY valid JSON
- No explanation text
- No markdown
- No comments
- No extra words

Node: {node_name}
Sector: {sector}

Generate up to {self.max_children} economic drivers influencing this node.

Rules:
- Only economic variables
- No company names
- No financial tickers
- Short names
- Label each as supply or demand

JSON format:
[
    {{"name": "...", "type": "supply"}},
    {{"name": "...", "type": "demand"}}
]
"""

        try:
            response = self.llm.invoke(prompt)
            parsed = self._safe_parse_json(response)
        except Exception:
            return self._fallback_generation(node_name)

        results = []
        for item in parsed[: self.max_children]:
            name = item.get("name", "").strip()
            t = item.get("type", "").lower()

            if not name:
                continue

            relation = "supply" if t == "supply" else "demand"
            results.append((name, relation))

        return results

    # SAFETY GUARDS
    def _is_valid_new_node(self, parent, child):
        """
        Prevent cycles, duplicates, nonsense.
        """

        if not child:
            return False

        if child == parent:
            return False

        if child in self.visited:
            return False

        if self.graph.has_node(child):
            return False

        if len(child) > 60:
            return False

        return True

    # SAFE JSON PARSER
    def _safe_parse_json(self, text):
        """
        Extract JSON from LLM response safely.
        """

        if isinstance(text, list):
            return text

        start = text.find("[")
        end = text.rfind("]") + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        return json.loads(text[start:end])

    # FALLBACK (NO LLM / FAILURE)
    def _fallback_generation(self, node):
        """
        Deterministic minimal expansion if LLM fails.
        """

        return [
            ("Input Cost Pressure", "supply"),
            ("Customer Demand Growth", "demand"),
        ]