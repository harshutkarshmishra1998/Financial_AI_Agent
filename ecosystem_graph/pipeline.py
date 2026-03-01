# ecosystem_graph/pipeline.py

from ecosystem_graph.data.market_universe import MarketUniverse
from ecosystem_graph.data.ontology import INDUSTRY_DEPENDENCY_PROFILE
from ecosystem_graph.core.graph_engine import EcosystemGraphEngine
from ecosystem_graph.core.propagation import PropagationEngine


class EcosystemPipeline:

    def __init__(self, universe_path):
        self.universe = MarketUniverse(universe_path)

    def run(self, symbol):

        company = self.universe.get_company(symbol)

        ticker = company["yfinance_symbol"]
        industry = company["nse_industry"]

        engine = EcosystemGraphEngine(ticker, industry)

        profile = INDUSTRY_DEPENDENCY_PROFILE.get(industry, {})

        propagation = PropagationEngine(engine)

        propagation.inject_industry_profile(profile)
        propagation.propagate_to_macro()
        propagation.propagate_policy()
        propagation.build_macro_network()

        nodes, edges = engine.export()

        return nodes, edges