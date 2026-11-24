import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ai_service.config import settings
from ai_service.rag.embedder import get_embedder
from ai_service.rag.document_loader import build_documents_from_subscriptions

logger = logging.getLogger(__name__)


class FAISSVectorStoreManager:
    """Manages per-user FAISS vector databases ensuring strict tenant isolation."""

    def __init__(self):
        self._user_stores: Dict[int, FAISS] = {}
        self._embedder = get_embedder()
        os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)

    def get_user_index_path(self, user_id: int) -> str:
        return os.path.join(settings.FAISS_INDEX_DIR, f"user_{user_id}")

    def index_subscriptions(self, user_id: int, subscriptions: List[Dict[str, Any]]) -> int:
        """Create or rebuild FAISS vector index for a specific user."""
        docs = build_documents_from_subscriptions(subscriptions, user_id)
        if not docs:
            self._user_stores.pop(user_id, None)
            path = self.get_user_index_path(user_id)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
            return 0

        vectorstore = FAISS.from_documents(docs, self._embedder)
        self._user_stores[user_id] = vectorstore

        try:
            path = self.get_user_index_path(user_id)
            vectorstore.save_local(path)
            logger.info("Persisted FAISS index for user %d with %d documents.", user_id, len(docs))
        except Exception as e:
            logger.warning("Failed to save FAISS index to disk for user %d: %s", user_id, e)

        return len(docs)

    def get_or_load_vectorstore(self, user_id: int, fallback_subscriptions: Optional[List[Dict[str, Any]]] = None) -> Optional[FAISS]:
        if user_id in self._user_stores:
            return self._user_stores[user_id]

        path = self.get_user_index_path(user_id)
        if os.path.exists(path) and os.path.exists(os.path.join(path, "index.faiss")):
            try:
                vs = FAISS.load_local(path, self._embedder, allow_dangerous_deserialization=True)
                self._user_stores[user_id] = vs
                return vs
            except Exception as e:
                logger.warning("Could not load FAISS index from disk for user %d: %s", user_id, e)

        if fallback_subscriptions:
            self.index_subscriptions(user_id, fallback_subscriptions)
            return self._user_stores.get(user_id)

        return None

    def similarity_search(
        self,
        user_id: int,
        query: str,
        k: Optional[int] = None,
        fallback_subscriptions: Optional[List[Dict[str, Any]]] = None
    ) -> List[Document]:
        """Perform semantic similarity search strictly scoped to the requested user_id."""
        k_val = k or settings.TOP_K_RETRIEVAL
        vs = self.get_or_load_vectorstore(user_id, fallback_subscriptions)
        if not vs:
            return []

        results = vs.similarity_search(query, k=k_val)
        isolated_results = [doc for doc in results if doc.metadata.get("user_id") == user_id]
        return isolated_results


vector_manager = FAISSVectorStoreManager()
