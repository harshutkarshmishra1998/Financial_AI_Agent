import hashlib
import os

import numpy as np


def _hash_to_vector(text: str, dim: int = 384) -> np.ndarray:
    """Deterministic fallback embedding without external APIs."""
    vec = np.zeros(dim, dtype="float32")
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[idx] += sign
    return vec


class Embedder:

    def __init__(self, model="text-embedding-3-small"):
        self.model_name = model
        self.model = None
        if os.getenv("OPENAI_API_KEY"):
            try:
                from langchain_openai import OpenAIEmbeddings

                self.model = OpenAIEmbeddings(model=model)
            except Exception:
                self.model = None

    def encode(self, texts):

        # Ensure list input
        if isinstance(texts, str):
            texts = [texts]

        # Get embeddings
        if self.model is not None:
            vectors = self.model.embed_documents(texts)
        else:
            vectors = [_hash_to_vector(t) for t in texts]

        # Convert to numpy
        vectors = np.array(vectors, dtype="float32")

        # Ensure 2D shape (N, D)
        vectors = np.atleast_2d(vectors)

        # Normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        vectors = vectors / norms

        return vectors
