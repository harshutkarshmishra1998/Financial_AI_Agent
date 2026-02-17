from langgraph.graph import StateGraph, END

from query_understanding.langgraph_node import (
    query_understanding_node,
    AgentState,
)

from query_enrichment.langgraph_node import query_enrichment_node


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("query_understanding", query_understanding_node)
    builder.add_node("query_enrichment", query_enrichment_node)

    builder.set_entry_point("query_understanding")
    builder.add_edge("query_understanding", "query_enrichment")
    builder.add_edge("query_enrichment", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke({
        "user_query": "How did gold market performed last week?",
        "enrichment_last_n": 1   # ✅ must match enrichment node
    })

    print(result)