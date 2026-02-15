from langgraph.graph import StateGraph, END
from query_understanding.langgraph_node import query_understanding_node, AgentState


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("query_understanding", query_understanding_node)
    builder.set_entry_point("query_understanding")
    builder.add_edge("query_understanding", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke({
        "user_query": "Why did Tesla stock rise last month?"
    })

    print(result)