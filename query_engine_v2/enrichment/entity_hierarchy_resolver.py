from typing import Dict, Any, List, Optional


# =========================================================
# HIERARCHY REGISTRIES (EXPAND OVER TIME)
# =========================================================

SECTOR_KEYWORDS = {
    "tech": {"sector": "technology"},
    "technology": {"sector": "technology"},
    "bank": {"sector": "banking"},
    "financial": {"sector": "financials"},
    "energy": {"sector": "energy"},
    "pharma": {"sector": "pharmaceuticals"},
    "healthcare": {"sector": "healthcare"},
    "auto": {"sector": "automobile"},
    "metals": {"sector": "metals"},
    "utilities": {"sector": "utilities"},
    "fmcg": {"sector": "consumer_goods"},
}

INDEX_KEYWORDS = {
    "s&p": {"index": "SPX"},
    "s&p 500": {"index": "SPX"},
    "nasdaq": {"index": "NASDAQ"},
    "dow": {"index": "DJI"},
    "sensex": {"index": "SENSEX"},
    "nifty": {"index": "NIFTY50"},
}

ASSET_CLASS_KEYWORDS = {
    "commodities": "commodity",
    "crypto": "crypto",
    "forex": "forex",
    "bonds": "bond"
}


# =========================================================
# RESOLUTION
# =========================================================

def resolve_entity_scope(record: Dict[str, Any]) -> Dict[str, Any]:

    query = record.get("user_query", "").lower()

    # default
    record["entity_scope_level"] = "single_asset"
    record["entity_expansion"] = None

    # ------------------------------
    # sector detection
    # ------------------------------
    for key, data in SECTOR_KEYWORDS.items():
        if key in query:
            record["entity_scope_level"] = "sector"
            record["entity_expansion"] = {
                "sector": data["sector"],
                "example_constituents": data["example_constituents"]
            }
            return record

    # ------------------------------
    # index detection
    # ------------------------------
    for key, data in INDEX_KEYWORDS.items():
        if key in query:
            record["entity_scope_level"] = "index"
            record["entity_expansion"] = data
            return record

    # ------------------------------
    # asset class detection
    # ------------------------------
    for key, asset_class in ASSET_CLASS_KEYWORDS.items():
        if key in query:
            record["entity_scope_level"] = "asset_class"
            record["entity_expansion"] = {
                "asset_class": asset_class
            }
            return record

    return record