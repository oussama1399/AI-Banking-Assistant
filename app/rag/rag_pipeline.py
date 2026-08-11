"""
RAG (Retrieval-Augmented Generation) pipeline for AI Banking Assistant
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI  # Or any other LLM you prefer
from langchain.prompts import PromptTemplate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankingRAGPipeline:
    """
    RAG pipeline for banking documentation retrieval
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG pipeline

        Args:
            persist_directory (str): Directory to store vector database
        """
        self.persist_directory = persist_directory
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
        self.embeddings_model = None

    def load_documents(self, docs_path: str = "./data/knowledge_base/") -> List[Dict[str, Any]]:
        """
        Load all markdown documents from the knowledge base

        Args:
            docs_path (str): Path to directory containing markdown files

        Returns:
            List of document dictionaries
        """
        try:
            # Find all markdown files
            markdown_files = glob.glob(os.path.join(docs_path, "*.md"))

            documents = []

            for file_path in markdown_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract filename without extension for metadata
                filename = os.path.basename(file_path)
                doc_dict = {
                    "content": content,
                    "metadata": {
                        "source": filename,
                        "type": "banking_document"
                    }
                }
                documents.append(doc_dict)

            logger.info(f"Loaded {len(documents)} documents from {docs_path}")
            return documents

        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise

    def create_vector_store(self, documents: List[Dict[str, Any]]) -> Chroma:
        """
        Create vector store from documents

        Args:
            documents (List[Dict]): List of document dictionaries

        Returns:
            Chroma vector store
        """
        try:
            # Initialize embeddings
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", " ", ""]
            )

            # Process all documents
            texts = []
            metadatas = []

            for doc in documents:
                chunks = text_splitter.split_text(doc["content"])
                texts.extend(chunks)

                # Add metadata to each chunk
                for _ in chunks:
                    metadatas.append(doc["metadata"])

            # Create vector store
            self.vector_store = Chroma.from_texts(
                texts=texts,
                metadatas=metadatas,
                embedding=self.embeddings_model,
                persist_directory=self.persist_directory
            )

            logger.info("Vector store created successfully")
            return self.vector_store

        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise

    def setup_retriever(self):
        """
        Setup the retriever for document retrieval
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")

        # Create retriever with similarity search
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}  # Return top 4 relevant documents
        )

        logger.info("Retriever setup complete")

    def setup_qa_chain(self):
        """
        Setup the QA chain for answering questions using retrieved documents
        """
        if self.retriever is None:
            raise ValueError("Retriever not initialized. Call setup_retriever first.")

        # Create a simple prompt template
        prompt_template = """Utilisez les éléments de contexte suivants pour répondre de manière claire et concise à la question.
        Si vous ne connaissez pas la réponse, dites-le simplement.

        Contexte: {context}

        Question: {question}

        Réponse claire et concise:"""

        prompt = PromptTemplate.from_template(prompt_template)

        # Create the QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0.1),  # You can change this to your preferred LLM
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        logger.info("QA chain setup complete")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant documents

        Args:
            query (str): Query to search for

        Returns:
            List of relevant documents
        """
        if self.retriever is None:
            raise ValueError("Retriever not initialized. Call setup_retriever first.")

        try:
            # Get relevant documents
            docs = self.retriever.get_relevant_documents(query)

            # Format results
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": getattr(doc, 'score', None)
                })

            return results

        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline

        Args:
            question (str): Question to answer

        Returns:
            Dictionary with answer and source documents
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call setup_qa_chain first.")

        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})

            return {
                "answer": result["result"],
                "source_documents": [doc.page_content for doc in result["source_documents"]],
                "metadata": [doc.metadata for doc in result["source_documents"]]
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def initialize_pipeline(self):
        """
        Complete initialization of the RAG pipeline
        """
        try:
            # Load documents
            documents = self.load_documents()

            # Create vector store
            self.create_vector_store(documents)

            # Setup retriever
            self.setup_retriever()

            # Setup QA chain
            self.setup_qa_chain()

            logger.info("RAG pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {e}")
            raise

# Example usage function
def test_rag_pipeline():
    """Test the RAG pipeline with sample questions"""
    try:
        # Initialize pipeline
        rag = BankingRAGPipeline()
        rag.initialize_pipeline()

        # Test questions
        test_questions = [
            "Quels sont les frais pour un virement international ?",
            "Quel est le plafond de ma carte Gold ?",
            "Comment ouvrir un compte bancaire ?"
        ]

        print("Testing RAG pipeline...")
        for question in test_questions:
            print(f"\nQuestion: {question}")
            result = rag.answer_question(question)
            print(f"Answer: {result['answer'][:200]}...")

    except Exception as e:
        print(f"Error in RAG test: {e}")

if __name__ == "__main__":
    test_rag_pipeline()