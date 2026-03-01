import networkx as nx
import matplotlib.pyplot as plt


def draw_ecosystem_graph(nodes, edges, output_file="ecosystem_v1.png"):

    G = nx.DiGraph()

    # -----------------------
    # Add Nodes
    # -----------------------
    node_colors = []

    color_map = {
        "company": "#1f77b4",   # blue
        "macro": "#ff7f0e",     # orange
        "global": "#2ca02c",    # green
        "policy": "#d62728",    # red
    }

    for n in nodes:
        node_id = n["node"]
        node_type = n.get("type", "macro")

        G.add_node(node_id, node_type=node_type)
        node_colors.append(color_map.get(node_type, "#7f7f7f"))

    # -----------------------
    # Add Edges
    # -----------------------
    for e in edges:
        G.add_edge(
            e["source"],
            e["target"],
            relation=e.get("relation", "")
        )

    # -----------------------
    # Layout
    # -----------------------
    plt.figure(figsize=(14, 8))

    pos = nx.spring_layout(G, k=1.2, iterations=100)

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors, #type: ignore
        node_size=3000
    )

    nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle="->",
        arrowsize=20,
        width=2
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=10,
        font_weight="bold"
    )

    # Edge labels
    edge_labels = nx.get_edge_attributes(G, "relation")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=8
    )

    plt.title("Financial Ecosystem Graph (v1)", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Graph saved to {output_file}")