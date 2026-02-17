from typing import TypedDict, List

class AgentState(TypedDict, total=False):
    user_query: str
    parsed_query: dict

    enrichment_last_n: int

    cleaned_records: int
    deleted_intermediate_files: List[str]