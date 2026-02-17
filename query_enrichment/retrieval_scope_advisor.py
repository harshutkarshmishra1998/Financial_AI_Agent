from typing import Dict


def recommend_scope(completeness: float, ambiguity: bool) -> Dict:

    if ambiguity:
        return {
            "scope": "broad",
            "search_expansion_level": 3,
        }

    if completeness > 0.8:
        return {
            "scope": "targeted",
            "search_expansion_level": 1,
        }

    if completeness > 0.5:
        return {
            "scope": "expanded",
            "search_expansion_level": 2,
        }

    return {
        "scope": "broad",
        "search_expansion_level": 3,
    }