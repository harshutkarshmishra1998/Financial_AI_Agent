from typing import TypedDict
from query_enrichment.pipeline import enrich_query


class AgentState(TypedDict, total=False):
    user_query: str
    parsed_query: dict
    enriched_query: dict
    enrichment_last_n: int
    enrichment_completed: bool


def query_enrichment_node(state: AgentState) -> AgentState:
    """
    Runs full enrichment pipeline on query logs.
    Works as a side-effect node (file IO based).
    """

    last_n = state.get("enrichment_last_n")

    enrich_query(last_n=last_n)

    state["enrichment_completed"] = True
    return state