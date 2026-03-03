
from multistream_researcher.query_builder import build_queries
from multistream_researcher.news_connectors.web_connector import search_and_load
from multistream_researcher.cleaners.financial_text_cleaner import clean_text
from multistream_researcher.chunking.domain_chunker import chunk_text
from multistream_researcher.embeddings.embedder import Embedder
from multistream_researcher.vector_store.faiss_store import FAISSStore
from multistream_researcher.compression.context_compressor import compress
from multistream_researcher.llm_driver_ranker import LLMDriverRanker

class Phase3Researcher:

    def __init__(self):
        self.embedder = Embedder()
        self.store = None
        self.driver_ranker = LLMDriverRanker()

    def ingest(self, anomaly_event, graph_nodes):
        selected_nodes = self.driver_ranker.rank(anomaly_event, graph_nodes)
        if not selected_nodes:
            selected_nodes = graph_nodes[:6]

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

        embeddings = self.embedder.encode(texts)

        self.store = FAISSStore(len(embeddings[0]))
        self.store.add(embeddings, texts, meta)
        print("Index dimension:", embeddings.shape)

    def retrieve(self, query):
        if self.store is None:
            raise RuntimeError("Index not initialized. Call ingest() before retrieve().")
        qemb = self.embedder.encode([query])
        # print("Query dimension:", qemb.shape)
        results = self.store.search(qemb, 5)
        texts = [r[0] for r in results]
        return compress(texts)
