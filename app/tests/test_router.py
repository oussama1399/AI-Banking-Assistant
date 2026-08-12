"""
Tests for the banking router.
"""

import pytest

from app.services.router import BankingRouter


@pytest.fixture
def router() -> BankingRouter:
    return BankingRouter()


class TestBalanceRoute:
    def test_solde(self, router):
        d = router.classify("C1024", "Quel est mon solde ?")
        assert d.route_type == "tool"
        assert d.tool == "get_account_balance"
        assert d.parameters["customer_id"] == "C1024"
        assert d.needs_rag is False


class TestTransferRoute:
    def test_transfer_status(self, router):
        d = router.classify("C1024", "Quel est le statut de mon virement TR4587 ?")
        assert d.tool == "get_transfer_status"
        assert d.parameters["transfer_id"] == "TR4587"
        assert d.route_type == "tool"
        assert d.needs_rag is False

    def test_transfer_rejected_uses_rag(self, router):
        d = router.classify(
            "C1024",
            "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?",
        )
        assert d.tool == "get_transfer_status"
        assert d.route_type == "tool+rag"
        assert d.needs_rag is True

    def test_transfer_without_id_needs_clarification(self, router):
        d = router.classify("C1024", "Quel est le statut de mon virement ?")
        assert d.is_clarification
        assert d.missing_parameter == "transfer_id"


class TestTransactionsRoute:
    def test_transactions(self, router):
        d = router.classify("C1024", "Quels sont mes derniers paiements ?")
        assert d.tool == "get_transactions"
        assert d.parameters["customer_id"] == "C1024"


class TestCardRoute:
    def test_card(self, router):
        d = router.classify("C1024", "Quel est le statut de ma carte ?")
        assert d.tool == "get_card_info"


class TestRAGRoute:
    def test_international_fees(self, router):
        d = router.classify(
            "C1024", "Quels sont les frais pour un virement international ?"
        )
        assert d.route_type == "rag"
        assert d.tool is None
        assert d.needs_rag is True

    def test_lost_card_procedure(self, router):
        d = router.classify("C1024", "Que faire en cas de perte de carte ?")
        assert d.route_type == "rag"
        assert d.needs_rag is True


class TestEdgeCases:
    def test_empty_message(self, router):
        d = router.classify("C1024", "")
        assert d.is_clarification

    def test_unknown_topic_falls_back_to_rag(self, router):
        d = router.classify("C1024", "Quelle est la politique de fraude ?")
        assert d.route_type == "rag"