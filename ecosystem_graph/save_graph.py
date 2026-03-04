import networkx as nx
import pickle

def save_graph_structure(nodes, edges, run_dir):
    G = nx.DiGraph()

    # Add nodes with attributes
    for n in nodes:
        node_name = n["node"]
        attrs = {k: v for k, v in n.items() if k != "node"}
        G.add_node(node_name, **attrs)

    # Add edges
    for e in edges:
        G.add_edge(e["source"], e["target"], relation=e.get("relation"))

    # 1. Save as Pickle (The replacement for gpickle)
    with open(run_dir / "ecosystem_graph.pkl", "wb") as f:
        pickle.dump(G, f)

    # 2. Save as GraphML (Great for visualization)
    nx.write_graphml(G, run_dir / "ecosystem_graph.graphml")

    # print(f"Graph structure saved to {run_dir}")