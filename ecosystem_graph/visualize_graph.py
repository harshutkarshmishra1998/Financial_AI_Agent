from pyvis.network import Network


def draw_ecosystem_graph(
    nodes,
    edges,
    output_file="data/ecosystem_interactive.html"
):
    """
    Interactive Financial Ecosystem Graph
    - hover edge to see relation
    - zoom / pan
    - physics layout
    - color legend
    """

    net = Network(
        height="900px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#000000" #type: ignore
    )

    # ---------------------------------------------------
    # Node Colors
    # ---------------------------------------------------
    node_colors = {
        "company": "#1f77b4",
        "macro": "#ff7f0e",
        "global": "#2ca02c",
        "policy": "#d62728",
        "supply": "#7f7f7f",
        "demand": "#bcbd22",
        "supplier": "#9467bd"
    }

    # ---------------------------------------------------
    # Add Nodes
    # ---------------------------------------------------
    for n in nodes:
        node_id = n["node"]
        node_type = n.get("type", "macro")

        net.add_node(
            node_id,
            label=node_id,
            color=node_colors.get(node_type, "#cccccc"),
            title=f"Type: {node_type}",   # hover tooltip
            size=20
        )

    # ---------------------------------------------------
    # Edge Colors by Relation
    # ---------------------------------------------------
    relation_colors = {
        "supply": "#1f77b4",
        "demand": "#ff7f0e",
        "competes_with": "#aaaaaa",
        "influenced_by": "#2ca02c",
        "impacts": "#2ca02c",
        "transmits_to": "#2ca02c",
        "regulated_by": "#d62728",
        "supplies_to": "#9467bd"
    }

    # ---------------------------------------------------
    # Add Edges
    # ---------------------------------------------------
    for e in edges:
        relation = e.get("relation", "")

        color = "#444444"
        for key, val in relation_colors.items():
            if key in relation:
                color = val
                break

        net.add_edge(
            e["source"],
            e["target"],
            title=relation,   # hover shows relation name
            color=color,
            arrows="to"
        )

    # ---------------------------------------------------
    # Physics Layout (nice separation)
    # ---------------------------------------------------
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )

    # ---------------------------------------------------
    # LEGEND (HTML overlay)
    # ---------------------------------------------------
    legend_html = """
    <div style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: white;
        padding: 12px;
        border: 1px solid #ccc;
        border-radius: 8px;
        font-family: Arial;
        font-size: 13px;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
        z-index: 9999;
    ">
    <b>Relation Types</b><br><br>

    <span style="color:#1f77b4;">■</span> Supply<br>
    <span style="color:#ff7f0e;">■</span> Demand<br>
    <span style="color:#2ca02c;">■</span> Influence / Impact / Transmission<br>
    <span style="color:#d62728;">■</span> Regulation<br>
    <span style="color:#aaaaaa;">■</span> Competition<br>
    <span style="color:#9467bd;">■</span> Supplier Link<br>
    <span style="color:#444444;">■</span> Other<br>
    </div>
    """

    net.set_options("""
    {
    "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true}
    }
    """)

    # net.show(output_file)
    net.write_html(output_file, open_browser=False, notebook=False)

    # inject legend into html
    with open(output_file, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("</body>", legend_html + "</body>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Interactive graph saved → {output_file}")