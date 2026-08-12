"""
RAG Service — wrapper around the BankingRAGPipeline.

Provides initialization, document retrieval, and graceful fallback
when the pipeline is not yet built or Chroma fails.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.monitoring.metrics import RAG_LATENCY, RAG_QUERIES_TOTAL

logger = logging.getLogger(__name__)


class RAGService:
    """Thin wrapper around the LangChain + Chroma RAG pipeline."""

    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        self.pipeline = None
        self.persist_directory = persist_directory
        self._initialized = False
        self._init_error: Optional[Exception] = None

    def initialize(self) -> None:
        """Lazy-load the pipeline. Idempotent; errors are captured."""
        if self._initialized:
            return
        try:
            from app.rag.rag_pipeline import BankingRAGPipeline

            self.pipeline = BankingRAGPipeline(persist_directory=self.persist_directory)
            self.pipeline.initialize_pipeline()
            self._initialized = True
            logger.info("RAG pipeline initialized successfully.")
        except Exception as e:
            self._init_error = e
            logger.exception("RAG pipeline failed to initialize: %s", e)

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Return up to ``k`` relevant documents for the given query."""
        if not self._initialized:
            self.initialize()
        if self.pipeline is None:
            RAG_QUERIES_TOTAL.labels(status="uninitialized").inc()
            return []
        t0 = time.perf_counter()
        try:
            results = self.pipeline.search(query)[:k]
            RAG_QUERIES_TOTAL.labels(status="success").inc()
            return results
        except Exception as e:
            logger.exception("RAG search failed: %s", e)
            RAG_QUERIES_TOTAL.labels(status="error").inc()
            return []
        finally:
            elapsed = time.perf_counter() - t0
            RAG_LATENCY.observe(elapsed)

    @property
    def is_ready(self) -> bool:
        return self._initialized and self.pipeline is not None


_default_rag: Optional[RAGService] = None


def get_default_rag() -> RAGService:
    global _default_rag
    if _default_rag is None:
        from app.core.config import settings

        _default_rag = RAGService(persist_directory=settings.CHROMA_DB_PATH)
    return _default_rag
