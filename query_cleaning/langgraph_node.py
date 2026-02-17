from typing import TypedDict, List
from agent_state import AgentState
from query_cleaning.cleaner import clean_last_n_entries


# class CleaningState(TypedDict, total=False):
#     enrichment_last_n: int
#     cleaned_records: int
#     deleted_intermediate_files: List[str]


def query_cleaning_node(state: AgentState) -> AgentState:
    last_n = state.get("enrichment_last_n", 0)

    result = clean_last_n_entries(last_n)

    return AgentState(
        cleaned_records=result["processed"],
        deleted_intermediate_files=result["deleted_files"],
    )