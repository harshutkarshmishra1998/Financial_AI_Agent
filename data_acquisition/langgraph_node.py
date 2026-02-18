from agent_state import AgentState
from data_acquisition.pipeline.main_acquisition_runner import process_last_n_queries


def acquisition_node(state: AgentState) -> AgentState:
    """
    Runs full multi-domain acquisition pipeline
    for last N query log entries.
    """

    last_n = state.get("enrichment_last_n", 0)

    if last_n <= 0:
        return AgentState(
            acquisition_processed=0,
            acquisition_summary=[]
        )

    results = process_last_n_queries(last_n)

    return AgentState(
        acquisition_processed=len(results),
        acquisition_summary=results
    )