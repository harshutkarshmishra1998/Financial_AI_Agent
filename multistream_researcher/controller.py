
from multistream_researcher.query_builder import build_queries
from multistream_researcher.news_connectors.web_connector import search_and_load
from multistream_researcher.cleaners.financial_text_cleaner import clean_text
from multistream_researcher.chunking.domain_chunker import chunk_text
from multistream_researcher.embeddings.embedder import Embedder
from multistream_researcher.vector_store.faiss_store import FAISSStore
from multistream_researcher.compression.context_compressor import compress

class Phase3Researcher:

    def __init__(self):
        self.embedder = Embedder()
        self.store = None

    def ingest(self, anomaly_event, graph_nodes):

        queries = build_queries(anomaly_event, graph_nodes)

        docs = []
        for q in queries[:10]:
            docs.extend(search_and_load(q))

        texts = []
        meta = []

        for d in docs:
            cleaned = clean_text(d["content"])
            chunks = chunk_text(cleaned)

            for c in chunks:
                texts.append(c)
                meta.append({
                    "url": d.get("url"),
                    "matched_nodes": [n for n in graph_nodes if n.lower() in c.lower()],
                    "credibility": 0.7
                })
        
        if not texts:
            raise RuntimeError(
                "No documents retrieved during ingestion. "
                "Check search connector or internet access."
            )

        embeddings = self.embedder.encode(texts)

        self.store = FAISSStore(len(embeddings[0]))
        self.store.add(embeddings, texts, meta)
        print("Index dimension:", embeddings.shape)

    def retrieve(self, query):
        qemb = self.embedder.encode([query])
        # print("Query dimension:", qemb.shape)
        results = self.store.search(qemb, 5)
        texts = [r[0] for r in results]
        return compress(texts)
