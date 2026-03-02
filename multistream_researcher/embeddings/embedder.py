import numpy as np
from langchain_openai import OpenAIEmbeddings
import api_keys


class Embedder:

    def __init__(self, model="text-embedding-3-small"):

        self.model = OpenAIEmbeddings(
            model=model,
        )

    def encode(self, texts):

        # Ensure list input
        if isinstance(texts, str):
            texts = [texts]

        # Get embeddings
        vectors = self.model.embed_documents(texts)

        # Convert to numpy
        vectors = np.array(vectors, dtype="float32")

        # Ensure 2D shape (N, D)
        vectors = np.atleast_2d(vectors)

        # Normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        vectors = vectors / norms

        return vectors