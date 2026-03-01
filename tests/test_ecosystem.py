from ecosystem_graph.pipeline import EcosystemPipeline

pipe = EcosystemPipeline("universe/market_universe.parquet")
nodes, edges = pipe.run("TCS.NS")

print(nodes)
print(edges)