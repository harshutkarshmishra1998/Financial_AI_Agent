
# Phase 3 — Multi Stream Financial Researcher

Graph-aware + time-aware RAG system for explaining anomaly events using:
- financial news
- policy releases
- macro data
- official announcements

INPUT
- anomaly record
- ecosystem graph nodes

OUTPUT
- cleaned, ranked context chunks

Driver filtering
- Before query fan-out, graph nodes are LLM-ranked and truncated (top-k) to reduce
  query explosion and external API overload.

Run example:
python example_run.py
