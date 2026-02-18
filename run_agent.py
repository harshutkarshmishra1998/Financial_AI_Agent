from langgraph.graph import StateGraph, END
from agent_state import AgentState
from query_understanding.langgraph_node import query_understanding_node
from query_enrichment.langgraph_node import query_enrichment_node
from query_cleaning.langgraph_node import query_cleaning_node

# -------------------------------------------------
# LOAD QUERIES
# -------------------------------------------------
# from pathlib import Path

# def load_queries(file_path: str):
#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(f"Query file not found: {file_path}")

#     with open(path, "r", encoding="utf-8") as f:
#         return [line.strip() for line in f if line.strip()]

# -------------------------------------------------
# GRAPH
# -------------------------------------------------
def build_graph():
    builder = StateGraph(AgentState)

    # -------------------------
    # nodes
    # -------------------------
    builder.add_node("query_understanding", query_understanding_node)
    builder.add_node("query_enrichment", query_enrichment_node)
    builder.add_node("query_cleaning", query_cleaning_node)

    # -------------------------
    # flow
    # -------------------------
    builder.set_entry_point("query_understanding")

    builder.add_edge("query_understanding", "query_enrichment")
    builder.add_edge("query_enrichment", "query_cleaning")
    builder.add_edge("query_cleaning", END)

    return builder.compile()


# -------------------------------------------------
# RUN
# -------------------------------------------------

if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke({
        "user_query": "How did silver market performed last week compared to gold?",
        "enrichment_last_n": 1   # used by cleaning + enrichment
    })

# if __name__ == "__main__":
#     graph = build_graph()

#     queries = load_queries("uploaded_files/queries.txt")

#     for i, query in enumerate(queries, start=1):
#         print(f"\n--- Running Query {i} ---")
#         print("Query:", query)

#         result = graph.invoke({
#             "user_query": query,
#             "enrichment_last_n": 1
#         })

#         print("Result:", result)
