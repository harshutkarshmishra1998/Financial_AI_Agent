# import json
# from pathlib import Path
# from typing import List, Dict, Any


# CONFIG_PATH = Path("data_acquisition/config/asset_proxy_registry.json")


# class AssetResolver:

#     def __init__(self):
#         with open(CONFIG_PATH) as f:
#             self.proxy_map = json.load(f)

#     def resolve(self, query: Dict[str, Any]) -> List[str]:
#         """
#         Returns list of tickers to fetch.
#         """

#         tickers = []

#         # 1 explicit asset tickers
#         for asset in query.get("assets", []):
#             if "ticker" in asset:
#                 tickers.append(asset["ticker"])

#         # 2 primary asset fallback
#         primary = query.get("primary_asset", {})
#         if "ticker" in primary:
#             tickers.append(primary["ticker"])

#         # 3 proxy resolution by scope
#         scope = query.get("entity_scope_level")

#         if not tickers and scope:
#             proxy = self.proxy_map.get(scope)
#             if proxy:
#                 tickers.extend(proxy)

#         return list(set(tickers))


from typing import Dict, List, Any


class AssetResolver:
    """
    Resolves assets from query into market-fetchable tickers.

    Resolution priority:
    1. Explicit ticker provided
    2. Asset name mapped to ticker
    3. Scope proxy (market / country)
    4. Empty if nothing resolvable
    """

    # -------------------------------------------------
    # NAME → TICKER MAPPING (extend anytime)
    # -------------------------------------------------
    NAME_TO_TICKER = {
        # commodities
        "gold": "XAUUSD",
        "silver": "XAGUSD",
        "crude oil": "CL=F",
        "oil": "CL=F",
        "natural gas": "NG=F",

        # indices
        "s&p 500": "SPY",
        "sp500": "SPY",
        "nasdaq": "QQQ",
        "dow": "DIA",

        # crypto common
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
    }

    # -------------------------------------------------
    # SCOPE → PROXY TICKER
    # -------------------------------------------------
    SCOPE_PROXY = {
        "india_market": "^NSEI",
        "us_market": "SPY",
        "global_market": "VT",
    }

    # -------------------------------------------------
    # PUBLIC RESOLVE
    # -------------------------------------------------
    def resolve(self, query: Dict[str, Any]) -> List[str]:

        resolved: List[str] = []

        # =================================================
        # 1. EXPLICIT ASSETS BLOCK
        # =================================================
        assets = query.get("assets", [])

        for asset in assets:

            # -----------------------------
            # explicit ticker
            # -----------------------------
            ticker = asset.get("ticker")
            if ticker:
                resolved.append(str(ticker).upper())
                continue

            # -----------------------------
            # asset name mapping
            # -----------------------------
            name = asset.get("name")
            if name:
                mapped = self._map_name_to_ticker(name)
                if mapped:
                    resolved.append(mapped)

        # =================================================
        # 2. SCOPE PROXY IF NOTHING RESOLVED
        # =================================================
        if not resolved:
            scope = query.get("entity_scope_level")
            if scope and scope in self.SCOPE_PROXY:
                resolved.append(self.SCOPE_PROXY[scope])

        # =================================================
        # 3. RETURN UNIQUE
        # =================================================
        return list(dict.fromkeys(resolved))

    # -------------------------------------------------
    # INTERNAL NAME MAPPING
    # -------------------------------------------------
    def _map_name_to_ticker(self, name: str) -> str | None:
        """
        Case-insensitive name lookup.
        """
        key = name.strip().lower()
        return self.NAME_TO_TICKER.get(key)
