from langgraph.graph import StateGraph, END
from query_understanding.langgraph_node import query_understanding_node, AgentState
from data_acquisition.langgraph_node import data_acquisition_node


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("query_understanding", query_understanding_node)
    builder.add_node("data_acquisition", data_acquisition_node)


    builder.set_entry_point("query_understanding")
    builder.add_edge("query_understanding", "data_acquisition")
    builder.add_edge("data_acquisition", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke({
        "user_query": "Why did HSBC drop in London trading?",
        "last_n_queries": 1
    })

    print(result)