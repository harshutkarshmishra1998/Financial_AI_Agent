from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict, total=False):
    user_query: str
    parsed_query: dict

    enrichment_last_n: int

    cleaned_records: int
    deleted_intermediate_files: List[str]

    acquisition_processed: int
    acquisition_summary: List[Dict[str, Any]]