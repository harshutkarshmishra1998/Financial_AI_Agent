from dataclasses import dataclass
from typing import Dict, List


# ---------- Sector → Base Dependency Mapping ----------

# ecosystem_graph/data/ontology.py

INDUSTRY_DEPENDENCY_PROFILE = {

    "Financial Services": {
        "macro": ["RBI Repo Rate", "System Liquidity", "Credit Growth"],
        "policy": ["Banking Regulation", "Capital Adequacy Norms"]
    },

    "Diversified": {
        "macro": ["GDP Growth"],
        "policy": ["Corporate Tax Policy"]
    },

    "Chemicals": {
        "supply": ["Crude Oil", "Natural Gas"],
        "global": ["Global Commodity Prices"],
        "macro": ["Industrial Production"]
    },

    "Capital Goods": {
        "demand": ["Infrastructure Spending", "Industrial Capex"],
        "macro": ["Interest Rates"]
    },

    "Healthcare": {
        "policy": ["Drug Pricing Regulation"],
        "macro": ["Healthcare Spending"],
        "global": ["Pharma Export Demand"]
    },

    "Consumer Services": {
        "demand": ["Urban Consumption"],
        "macro": ["Disposable Income"]
    },

    "Forest Materials": {
        "supply": ["Timber Prices"],
        "policy": ["Environmental Regulation"]
    },

    "Construction Materials": {
        "supply": ["Limestone", "Energy"],
        "demand": ["Real Estate Activity", "Infrastructure Spending"]
    },

    "Power": {
        "supply": ["Coal", "Natural Gas"],
        "policy": ["Power Tariff Regulation"],
        "macro": ["Industrial Demand"]
    },

    "Metals & Mining": {
        "supply": ["Iron Ore", "Coal"],
        "global": ["China Demand", "Commodity Cycle"]
    },

    "Services": {
        "macro": ["GDP Growth", "Urbanization"]
    },

    "Oil Gas & Consumable Fuels": {
        "supply": ["Crude Oil"],
        "global": ["OPEC Production"],
        "macro": ["USD/INR"],
        "policy": ["Fuel Tax"]
    },

    "Construction": {
        "demand": ["Infrastructure Spending", "Real Estate"]
    },

    "Information Technology": {
        "global": ["US Tech Spending"],
        "macro": ["USD/INR"]
    },

    "Consumer Durables": {
        "demand": ["Urban Consumption"],
        "macro": ["Interest Rates"]
    },

    "Textiles": {
        "supply": ["Cotton Prices"],
        "global": ["Export Demand"]
    },

    "Realty": {
        "macro": ["Interest Rates"],
        "demand": ["Housing Demand"]
    },

    "Automobile and Auto Components": {
        "supply": ["Steel", "Aluminum"],
        "demand": ["Vehicle Demand"],
        "macro": ["Interest Rates"]
    },

    "Fast Moving Consumer Goods": {
        "demand": ["Rural Demand", "Urban Consumption"],
        "macro": ["CPI Inflation"]
    },

    "Telecommunication": {
        "macro": ["Data Consumption"],
        "policy": ["Spectrum Regulation"]
    },

    "Media Entertainment & Publication": {
        "demand": ["Advertising Spending"],
        "macro": ["Consumer Sentiment"]
    }
}