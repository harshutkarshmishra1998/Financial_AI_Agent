from typing import TypedDict
from .pipeline import process_data_acquisition


class AgentState(TypedDict, total=False):
    last_n_queries: int
    data_acquisition: dict


def data_acquisition_node(state: AgentState) -> AgentState:

    n = state.get("last_n_queries", 1)

    result = process_data_acquisition(n)

    state["data_acquisition"] = result.model_dump()

    return state