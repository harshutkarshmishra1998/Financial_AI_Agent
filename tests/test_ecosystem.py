from ecosystem_graph.pipeline import EcosystemPipeline
from ecosystem_graph.visualize_graph import draw_ecosystem_graph

pipe = EcosystemPipeline("universe/market_universe.parquet")
nodes, edges = pipe.run("RELIANCE.NS")

print(nodes)
print(edges)

draw_ecosystem_graph(nodes, edges)