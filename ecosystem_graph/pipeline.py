# ecosystem_graph/pipeline.py
import pandas as pd
from ecosystem_graph.data.market_universe import MarketUniverse
from ecosystem_graph.data.ontology import INDUSTRY_DEPENDENCY_PROFILE
from ecosystem_graph.core.graph_engine import EcosystemGraphEngine
from ecosystem_graph.core.propagation import PropagationEngine


class EcosystemPipeline:

    def __init__(self, universe_path):
        self.universe = MarketUniverse(universe_path)

    def _inject_sector_competitors(self, engine, symbol, industry):
        """
        Add competitor relationships sorted by company age
        (older listings first).
        """

        target_company = self.universe.get_company(symbol)
        target_ticker = target_company["yfinance_symbol"]

        universe_df = self.universe.df.copy()

        # Ensure datetime
        universe_df["data_start"] = pd.to_datetime(
            universe_df["data_start"], errors="coerce"
        )

        # Filter same industry excluding target
        peers_df = universe_df[
            (universe_df["nse_industry"] == industry) &
            (universe_df["symbol"] != symbol)
        ].copy()

        # Sort by oldest first
        peers_df = peers_df.sort_values("data_start", ascending=True)

        # Optional: limit number of competitors (recommended)
        MAX_COMPETITORS = 15
        peers_df = peers_df.head(MAX_COMPETITORS)

        for _, row in peers_df.iterrows():
            peer_ticker = row["yfinance_symbol"]

            # Prevent self-loop just in case
            if peer_ticker == target_ticker:
                continue

            engine._add_edge(target_ticker, peer_ticker, "competes_with")
            engine._add_edge(peer_ticker, target_ticker, "competes_with")

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

        self._inject_sector_competitors(engine, symbol, industry)

        nodes, edges = engine.export()

        return nodes, edges