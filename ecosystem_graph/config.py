from __future__ import annotations

INDIAN_STRUCTURAL_DRIVERS = {
    "monetary": ["RBI repo rate", "G-Sec yields", "Liquidity surplus/deficit"],
    "currency": ["USD/INR", "Forex reserves"],
    "capital_flow": ["FII inflow/outflow", "DII absorption"],
    "real_economy": ["GST collections", "CPI inflation", "IIP", "Rural demand"],
    "policy": ["Union Budget", "Import/export duties", "Sector subsidies", "SEBI regulations"],
}

GLOBAL_DRIVERS = [
    "Brent crude",
    "US Fed rates",
    "Dollar Index",
    "China demand",
    "OPEC production decisions",
]

DEFAULT_COMPETITOR_LIMIT = 5
