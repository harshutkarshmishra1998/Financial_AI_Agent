
import faiss
import numpy as np

class FAISSStore:

    def __init__(self, dim):
        self.index = faiss.IndexFlatIP(dim)
        self.texts = []
        self.meta = []

    def add(self, embeddings, texts, meta):
        self.index.add(np.array(embeddings).astype("float32"))
        self.texts.extend(texts)
        self.meta.extend(meta)

    def search(self, query_emb, k=5):
        if not self.texts:
            return []
        k = min(k, len(self.texts))
        D, I = self.index.search(query_emb, k)
        results = []
        for idx in I[0]:
            if idx < 0:
                continue
            results.append((self.texts[idx], self.meta[idx]))
        return results
