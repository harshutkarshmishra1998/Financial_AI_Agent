import os
from data.market_universe import MarketUniverse
from core.graph_builder import GraphBuilder
from core.graph_expander import GraphExpander
from core.graph_validator import GraphValidator
from llm.groq_extractor import GroqExtractor


class EcosystemPipeline:

    def __init__(self, universe_path, groq_key=None):
        self.universe = MarketUniverse(universe_path)
        self.llm = GroqExtractor(groq_key) if groq_key else None

    def run(self, symbol, output_dir="graph_output"):

        self.universe.validate_symbol(symbol)
        info = self.universe.get_company_info(symbol)

        builder = GraphBuilder(symbol, info["sector"])
        expander = GraphExpander(builder, self.universe, self.llm)

        expander.expand_supply()
        expander.expand_competitors()
        expander.inject_macro()
        expander.inject_policy()
        expander.expand_llm()

        validator = GraphValidator(builder)
        validator.ensure_macro_presence()

        nodes_df, edges_df = validator.to_dataframes()

        os.makedirs(output_dir, exist_ok=True)
        nodes_df.to_parquet(f"{output_dir}/nodes.parquet")
        edges_df.to_parquet(f"{output_dir}/edges.parquet")

        graph_hash = builder.hash_graph()
        with open(f"{output_dir}/hash.txt", "w") as f:
            f.write(graph_hash)

        print("Graph built successfully")
        print("Nodes:", len(nodes_df))
        print("Edges:", len(edges_df))
        print("Hash:", graph_hash)