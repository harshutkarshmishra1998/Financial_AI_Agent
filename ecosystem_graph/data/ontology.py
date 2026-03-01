from dataclasses import dataclass
from typing import Dict, List


# ---------- Sector → Base Dependency Mapping ----------

SECTOR_DEPENDENCIES = {
    "Refining": ["Brent Crude"],
    "Steel": ["Iron Ore", "Coking Coal"],
    "Cement": ["Limestone", "Energy"],
    "FMCG": ["Agri Commodities"],
    "IT": ["Global Demand", "USD/INR"],
    "Banking": ["Interest Rates", "System Liquidity"]
}


# ---------- Indian Macro Nodes ----------

INDIA_MACRO = [
    "RBI Repo Rate",
    "G-Sec Yield",
    "System Liquidity",
    "USD/INR",
    "Forex Reserves",
    "FII Flow",
    "DII Flow",
    "CPI Inflation",
    "GST Collections",
    "IIP",
    "Rural Demand"
]


# ---------- Global Macro Nodes ----------

GLOBAL_MACRO = [
    "Brent Crude",
    "US Fed Rate",
    "Dollar Index",
    "China Demand",
    "OPEC Production"
]


# ---------- Policy Nodes ----------

POLICY_NODES = [
    "Union Budget",
    "Import Duties",
    "Export Duties",
    "Sector Subsidies",
    "SEBI Regulation"
]


# ---------- Relationship Types ----------

REL_TYPES = {
    "INPUT": "consumes",
    "OUTPUT": "produces",
    "MACRO": "influenced_by",
    "POLICY": "regulated_by",
    "COMPETITOR": "competes_with"
}