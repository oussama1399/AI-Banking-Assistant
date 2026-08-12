"""
RAG (Retrieval-Augmented Generation) pipeline for AI Banking Assistant.
"""

from __future__ import annotations

import glob
import logging
import os
from typing import Any, Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    # LangChain >=0.2 split Chroma into its own package.
    from langchain_chroma import Chroma
except ImportError:  # pragma: no cover
    from langchain_community.vectorstores import Chroma  # type: ignore

from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class BankingRAGPipeline:
    """RAG pipeline for the banking knowledge base.

    Builds a Chroma vector store from local markdown documents,
    using a small HuggingFace embedding model. Provides a ``search``
    method returning the top-k chunks for a query.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        self.vector_store: Optional[Chroma] = None
        self.retriever = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None

    # --- Document loading -------------------------------------------------

    def load_documents(
        self, docs_path: str = "./data/knowledge_base/"
    ) -> List[Dict[str, Any]]:
        markdown_files = sorted(glob.glob(os.path.join(docs_path, "*.md")))
        documents: List[Dict[str, Any]] = []
        for file_path in markdown_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError as e:
                logger.warning("Cannot read %s: %s", file_path, e)
                continue
            documents.append(
                {
                    "content": content,
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "type": "banking_document",
                    },
                }
            )
        logger.info("Loaded %d documents from %s", len(documents), docs_path)
        return documents

    # --- Vector store -----------------------------------------------------

    def create_vector_store(self, documents: List[Dict[str, Any]]) -> Chroma:
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
        )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""],
        )

        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        for doc in documents:
            chunks = text_splitter.split_text(doc["content"])
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append(doc["metadata"])

        # Reuse the persisted DB if it already contains data, otherwise
        # create a new one from the texts.
        if texts:
            self.vector_store = Chroma.from_texts(
                texts=texts,
                metadatas=metadatas,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
            )
        else:
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

        logger.info("Vector store created (chunks=%d).", len(texts))
        return self.vector_store

    # --- Retriever --------------------------------------------------------

    def setup_retriever(self, k: int = 4) -> None:
        if self.vector_store is None:
            raise ValueError(
                "Vector store not initialized. Call create_vector_store first."
            )
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
        logger.info("Retriever ready (k=%d).", k)

    # --- Search -----------------------------------------------------------

    def search(self, query: str) -> List[Dict[str, Any]]:
        if self.retriever is None:
            raise ValueError(
                "Retriever not initialized. Call setup_retriever first."
            )
        docs = self.retriever.invoke(query)
        results: List[Dict[str, Any]] = []
        for doc in docs:
            results.append(
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": getattr(doc, "score", None),
                }
            )
        return results

    # --- End-to-end init --------------------------------------------------

    def initialize_pipeline(self) -> None:
        documents = self.load_documents()
        if not documents:
            logger.warning("No documents found; RAG will be empty.")
        self.create_vector_store(documents)
        self.setup_retriever()


# --- Tiny smoke test -------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    rag = BankingRAGPipeline()
    rag.initialize_pipeline()
    for q in [
        "Quels sont les frais pour un virement international ?",
        "Comment ouvrir un compte ?",
        "Que faire en cas de perte de carte ?",
    ]:
        results = rag.search(q)
        print(f"\nQ: {q}")
        for r in results[:2]:
            print(f"  - {r['metadata'].get('source')}: {r['content'][:120]}...")
