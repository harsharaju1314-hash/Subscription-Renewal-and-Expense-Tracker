import hashlib
import re
import numpy as np
from typing import List
from langchain_core.embeddings import Embeddings

from ai_service.config import settings


class DeterministicFinancialEmbeddings(Embeddings):
    """Deterministic, offline-safe embedding generator that maps financial text to 1536-dim unit vectors."""
    def __init__(self, dimension: int = 1536):
        self.dim = dimension

    def _embed_text(self, text: str) -> List[float]:
        tokens = re.findall(r"\w+", text.lower())
        vec = np.zeros(self.dim, dtype=np.float32)

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            weight = 1.0 + (len(token) / 10.0)
            vec[idx] += weight

            idx_sub = (h >> 16) % self.dim
            vec[idx_sub] += weight * 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)


def get_embedder() -> Embeddings:
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith("sk-"):
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        except Exception:
            return DeterministicFinancialEmbeddings(dimension=settings.EMBEDDING_DIM)
    return DeterministicFinancialEmbeddings(dimension=settings.EMBEDDING_DIM)
