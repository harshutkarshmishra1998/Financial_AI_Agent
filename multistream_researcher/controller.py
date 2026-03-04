from collections import Counter

from multistream_researcher.query_builder import build_queries
from multistream_researcher.news_connectors.web_connector import search_and_load
from multistream_researcher.cleaners.financial_text_cleaner import clean_text
from multistream_researcher.chunking.domain_chunker import chunk_text
from multistream_researcher.llm_driver_ranker import LLMDriverRanker

class Phase3Researcher:

    def __init__(self):
        self.texts = []
        self.meta = []
        self.driver_ranker = LLMDriverRanker()

    def ingest(self, anomaly_event, graph_nodes):
        original_nodes = len(graph_nodes)
        selected_nodes = self.driver_ranker.rank(anomaly_event, graph_nodes)
        if not selected_nodes:
            selected_nodes = graph_nodes[:6]

        print(
            f"Node filter summary → original: {original_nodes}, "
            f"selected for retrieval: {len(selected_nodes)}"
        )

        queries = build_queries(anomaly_event, selected_nodes)

        docs = []
        for q in queries[:10]:
            docs.extend(search_and_load(q))

        if not docs:
            docs = [{
                "content": (
                    f"No web documents were fetched for {anomaly_event.get('symbol', 'unknown symbol')} "
                    f"around {anomaly_event.get('timestamp', 'unknown date')}. "
                    f"Tracked graph nodes: {', '.join(selected_nodes)}."
                ),
                "url": None,
            }]

        texts = []
        meta = []

        for d in docs:
            cleaned = clean_text(d["content"])
            chunks = chunk_text(cleaned)

            for c in chunks:
                texts.append(c)
                meta.append({
                    "url": d.get("url"),
                    "matched_nodes": [n for n in selected_nodes if n.lower() in c.lower()],
                    "credibility": 0.7
                })
        
        if not texts:
            raise RuntimeError("No usable text generated during ingestion.")

        self.texts = texts
        self.meta = meta
        return selected_nodes

    def _score_text(self, text, query_tokens):
        token_counts = Counter(text.lower().split())
        return sum(token_counts[tok] for tok in query_tokens)

    def retrieve(self, query):
        if not self.texts:
            raise RuntimeError("Retriever not initialized. Call ingest() before retrieve().")

        query_tokens = [t.strip().lower() for t in query.split() if t.strip()]
        ranked = sorted(
            self.texts,
            key=lambda text: self._score_text(text, query_tokens),
            reverse=True,
        )
        return ranked[:5]
