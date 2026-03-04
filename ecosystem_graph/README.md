# Ecosystem Graph Module

The `ecosystem_graph` module builds a directed causal/company ecosystem graph around an anomalous symbol. It combines ontology-based propagation, peer relationships, and LLM-driven expansion.

## What this module does
- Loads company + industry context from market universe data.
- Initializes a root graph for target ticker.
- Injects known industry dependency ontology.
- Propagates to macro/policy layers.
- Adds same-industry competitors.
- Expands supply-demand drivers via LLM with graph safety controls.
- Expands supplier/customer/strategic dependencies via ontology-validated LLM outputs.
- Saves graph as interactive HTML + GraphML + pickle.

## Main orchestrator
### `pipeline.py`
- `EcosystemPipeline.__init__(universe_path, run_id=None)`
  - Loads market universe and sets output directory (`data/<run_id>/graph_outputs`).
- `_inject_sector_competitors(engine, symbol, industry)`
  - Adds bidirectional `competes_with` edges to up to 15 same-industry peers ordered by oldest listing date.
- `run(symbol)`
  - Main flow:
    1. Resolve target company + industry.
    2. Create `EcosystemGraphEngine`.
    3. Inject ontology profile + macro/policy propagation.
    4. Add competitor edges.
    5. Run `SupplyDemandExpander`.
    6. Run `CompanyDependencyExpander`.
    7. Export + save visual/serialized outputs.

## Core graph layer
### `core/graph_engine.py`
- `EcosystemGraphEngine`
  - Internal directed graph wrapper (`networkx.DiGraph`).
  - Methods:
    - `_add_node(name, node_type)`
    - `_add_edge(src, dst, relation)` with self-loop guard
    - `has_node(name)`
    - `add_dependency(node, node_type, relation)` (from root)
    - `add_transmission(src, dst, dst_type, relation)`
    - `get_hash()` hash over sorted node names
    - `export()` to list-of-dict nodes/edges format

### `core/propagation.py`
- `PropagationEngine`
  - `inject_industry_profile(profile)`
    - Adds profile nodes with dependency relation categories.
  - `propagate_to_macro()`
    - Adds macro transmission links for known macro/global nodes.
  - `propagate_policy()`
    - Adds policy influence links for policy-trigger nodes.
  - `build_macro_network()`
    - Adds fixed canonical macro causal links (repo→liquidity, fed→dollar, brent→USDINR).

## LLM integration
### `groq_client.py`
- `GroqLLM`
  - Thin adapter exposing `.invoke(prompt)` over Groq chat completions.
  - Defaults: model `llama-3.3-70b-versatile`, temperature `0.2`.

## Expansion engines
### `expansion/supply_demand_expander.py`
- `SupplyDemandExpander`
  - Breadth-first recursive node expansion with hard constraints:
    - max depth
    - max children per node
    - no cycles/duplicates
  - `expand(root_node, sector)` queue-based traversal.
  - `_generate_children(node_name, sector)` LLM prompt + parsing into `(name, relation)` tuples.
  - `_is_valid_new_node(parent, child)` guards (empty/self/visited/existing/too long).
  - `_safe_parse_json(text)` extracts JSON list safely from LLM text.
  - `_fallback_generation(node)` deterministic fallback when LLM fails.

### `expansion/company_dependency_expander.py`
- `CompanyDependencyExpander`
  - Hybrid approach: LLM generation + ontology validation.
  - `expand(company_ticker, sector)` runs only if sector rules exist.
  - `_llm_generate(company, sector)` asks for supplier/customer/strategic lists.
  - `_validate(raw, allowed)` filters to allowed semantic categories.
  - `_matches_allowed_category(name, allowed_types)` lightweight keyword matcher.
  - `_insert(company, deps)` inserts nodes and relation edges (`supplies_to`, `sells_to`, `strategic_dependency`).
  - `_safe_json(text)` extracts JSON object from model output.

## Data assets
### `data/market_universe.py`
- `MarketUniverse`
  - Loads parquet universe DataFrame.
  - `get_company(symbol)` returns first matching row or raises if missing.

### `data/ontology.py`
- `INDUSTRY_DEPENDENCY_PROFILE`
  - Manual ontology mapping industry -> dependency categories and base nodes.

### `data/macro_nodes.py`
- Lists used by propagation layer:
  - `INDIA_MACRO`, `GLOBAL_MACRO`, `POLICY_NODES`, and relation map `REL_TYPES`.

### `data/company_dependence_rules.py`
- `ALLOWED_DEPENDENCIES`
  - Sector-specific allowed dependency category vocab used for LLM output validation.

## Output helpers
### `visualize_graph.py`
- `draw_ecosystem_graph(nodes, edges, graph_dir)`
  - Builds interactive PyVis HTML with color-coded node/edge types and legend injection.

### `save_graph.py`
- `save_graph_structure(nodes, edges, run_dir)`
  - Writes NetworkX graph to:
    - pickle (`ecosystem_graph.pkl`)
    - graphml (`ecosystem_graph.graphml`)

## Practical notes
- Expansion depends on API keys/network; fallback logic is present in expansion modules.
- Graph node names mix companies, macro variables, policy factors, and synthetic drivers.
- GraphML output is consumed by `multistream_researcher` and `reasoning` modules.
