import pickle
import networkx as nx
from pathlib import Path

from ecosystem_graph.visualize_graph import draw_ecosystem_graph

def test_graph_files(run_dir):
    run_dir = Path(run_dir)
    
    # --- 1. Load from Pickle (.pkl) ---
    print("Loading from Pickle...")
    with open(run_dir / "ecosystem_graph.pkl", "rb") as f:
        G_pkl = pickle.load(f)
    
    # Extract nodes and edges back into list-of-dict format
    nodes_pkl = [{"node": n, **data} for n, data in G_pkl.nodes(data=True)]
    edges_pkl = [
        {"source": u, "target": v, "relation": data.get("relation")} 
        for u, v, data in G_pkl.edges(data=True)
    ]
    
    # Call your drawing function
    draw_ecosystem_graph(nodes_pkl, edges_pkl, output_file="data/pkl_test_interactive.html")

    # --- 2. Load from GraphML (.graphml) ---
    print("Loading from GraphML...")
    G_ml = nx.read_graphml(run_dir / "ecosystem_graph.graphml")
    
    nodes_ml = [{"node": n, **data} for n, data in G_ml.nodes(data=True)]
    edges_ml = [
        {"source": u, "target": v, "relation": data.get("relation")} 
        for u, v, data in G_ml.edges(data=True)
    ]
    
    draw_ecosystem_graph(nodes_ml, edges_ml, output_file="data/graphml_test_interactive.html")

    print("Test complete. Check the data/ folder for HTML files.")

if __name__ == "__main__":
    test_graph_files("data/run_4a4d530b49c7")