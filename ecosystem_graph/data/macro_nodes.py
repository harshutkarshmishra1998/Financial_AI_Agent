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

GLOBAL_MACRO = [
    "Brent Crude",
    "US Fed Rate",
    "Dollar Index",
    "China Demand",
    "OPEC Production"
]

POLICY_NODES = [
    "Union Budget",
    "Import Duties",
    "Export Duties",
    "Sector Subsidies",
    "SEBI Regulation"
]

REL_TYPES = {
    "INPUT": "consumes",
    "OUTPUT": "produces",
    "MACRO": "influenced_by",
    "POLICY": "regulated_by",
    "COMPETITOR": "competes_with"
}