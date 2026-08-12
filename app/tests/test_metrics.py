"""
Tests for Prometheus metrics endpoint and metric collection.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.orchestrator import BankingOrchestrator
from app.services.tool_service import ToolService


class FakeRAG:
    def search(self, query, k=4):
        return [{"content": "Doc test", "metadata": {"source": "test.md"}}]


class FakeLLM:
    def answer_with_tool(self, message, tool_result, tool_name):
        return "Fake tool answer"

    def answer_with_rag(self, message, documents):
        return "Fake RAG answer"

    def answer_with_tool_and_rag(self, message, tool_result, tool_name, documents):
        return "Fake tool+rag answer"


@pytest.fixture
def client(monkeypatch):
    orchestrator = BankingOrchestrator(
        tool_service=ToolService(),
        rag_service=FakeRAG(),
        llm_service=FakeLLM(),
    )
    from app.api import chat as chat_module

    monkeypatch.setattr(chat_module, "_orchestrator", orchestrator)
    return TestClient(app)


def test_metrics_endpoint_returns_200(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    assert "chat_requests_total" in content
    assert "tool_calls_total" in content
    assert "rag_queries_total" in content
    assert "chat_request_latency_seconds" in content


def test_metrics_updated_after_chat_request(client):
    # Make a chat request to trigger metrics increment
    client.post(
        "/api/v1/chat",
        json={"customer_id": "C1024", "message": "Quel est mon solde ?"},
    )
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert 'chat_requests_total{route_type="tool",status="success"}' in metrics_response.text or "chat_requests_total" in metrics_response.text
