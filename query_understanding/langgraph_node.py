from typing import TypedDict
from agent_state import AgentState
from query_understanding.pipeline import process_query


# class AgentState(TypedDict, total=False):
#     user_query: str
#     parsed_query: dict


def query_understanding_node(state: AgentState) -> AgentState:
    result = process_query(state["user_query"]) #type: ignore
    state["parsed_query"] = result.model_dump()
    return state