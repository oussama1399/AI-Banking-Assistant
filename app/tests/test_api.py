"""
End-to-end tests for the /chat API endpoint.

Uses FastAPI's TestClient. The orchestrator is instantiated with a
stub RAG + LLM to keep tests fast and offline.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.orchestrator import BankingOrchestrator
from app.services.tool_service import ToolService


class FakeRAG:
    def __init__(self, documents=None):
        self.documents = documents or [
            {
                "content": "Les virements internationaux incluent des frais.",
                "metadata": {"source": "international_transfer_fees.md"},
            }
        ]

    def search(self, query, k=4):
        return self.documents[:k]


class FakeLLM:
    def answer_with_tool(self, message, tool_result, tool_name):
        return f"[TOOL:{tool_name}] {message} → {tool_result}"

    def answer_with_rag(self, message, documents):
        if not documents:
            return "Aucun document pertinent trouvé."
        return f"[RAG] {message} (source: {documents[0]['metadata'].get('source')})"

    def answer_with_tool_and_rag(self, message, tool_result, tool_name, documents):
        return f"[TOOL+RAG] {message} → tool={tool_result}, docs={len(documents)}"


@pytest.fixture
def client(monkeypatch):
    fake_rag = FakeRAG()
    fake_llm = FakeLLM()
    orchestrator = BankingOrchestrator(
        router=orchestrator_default_router(),
        tool_service=ToolService(),
        rag_service=fake_rag,
        llm_service=fake_llm,
    )
    # Patch the lazy orchestrator in the API module.
    from app.api import chat as chat_module

    monkeypatch.setattr(chat_module, "_orchestrator", orchestrator)
    return TestClient(app)


def orchestrator_default_router():
    from app.services.router import BankingRouter
    return BankingRouter()


class TestChatEndpoint:
    def test_tool_only_balance(self, client):
        r = client.post(
            "/api/v1/chat",
            json={"customer_id": "C1024", "message": "Quel est mon solde ?"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["source"] == "get_account_balance"
        assert "TOOL:get_account_balance" in data["answer"]

    def test_rag_only(self, client):
        r = client.post(
            "/api/v1/chat",
            json={
                "customer_id": "C1024",
                "message": "Quels sont les frais pour un virement international ?",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["source"] == "RAG"
        assert data["documents"] is not None
        assert "international_transfer_fees.md" in data["documents"]

    def test_tool_plus_rag(self, client):
        r = client.post(
            "/api/v1/chat",
            json={
                "customer_id": "C1024",
                "message": "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["source"] == "get_transfer_status+RAG"
        assert "TOOL+RAG" in data["answer"]

    def test_clarification_missing_transfer_id(self, client):
        r = client.post(
            "/api/v1/chat",
            json={
                "customer_id": "C1024",
                "message": "Quel est le statut de mon virement ?",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["source"] == "clarification"
        assert "identifiant" in data["answer"].lower()

    def test_unknown_customer_returns_error_message(self, client):
        r = client.post(
            "/api/v1/chat",
            json={"customer_id": "C9999", "message": "Quel est mon solde ?"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["source"] == "error"
        assert "introuvable" in data["answer"].lower() or "associé" in data["answer"].lower()

    def test_health_endpoint(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"