"""
Tests for the banking tools (mock CSV-backed functions).
"""

import pytest

from app.tools import banking_tools


class TestAccountBalance:
    def test_existing_customer(self):
        result = banking_tools.get_account_balance("C1024")
        assert result["customer_id"] == "C1024"
        assert result["available_balance"] == 2450.75
        assert result["currency"] == "EUR"

    def test_unknown_customer_raises(self):
        with pytest.raises(Exception) as exc:
            banking_tools.get_account_balance("C9999")
        assert "customer_not_found" in str(exc.value)


class TestTransactions:
    def test_existing_customer_returns_list(self):
        txs = banking_tools.get_transactions("C1024")
        assert isinstance(txs, list)
        assert len(txs) >= 1
        assert "transaction_id" in txs[0]
        assert "amount" in txs[0]

    def test_unknown_customer_returns_empty(self):
        txs = banking_tools.get_transactions("C9999")
        assert txs == []


class TestCardInfo:
    def test_existing_customer(self):
        info = banking_tools.get_card_info("C1024")
        assert info["customer_id"] == "C1024"
        assert info["card_type"] == "Gold"

    def test_unknown_customer_raises(self):
        with pytest.raises(Exception) as exc:
            banking_tools.get_card_info("C9999")
        assert "customer_not_found" in str(exc.value)


class TestTransferStatus:
    def test_existing_transfer(self):
        info = banking_tools.get_transfer_status("TR4587")
        assert info["transfer_id"] == "TR4587"
        assert info["status"] in ("pending", "completed", "rejected")

    def test_unknown_transfer_raises(self):
        with pytest.raises(Exception) as exc:
            banking_tools.get_transfer_status("TR9999")
        assert "transfer_not_found" in str(exc.value)


class TestCustomerInfo:
    def test_existing_customer(self):
        info = banking_tools.get_customer_info("C1024")
        assert info["name"] == "Jean Martin"
        assert info["account_status"] == "active"

    def test_unknown_customer_raises(self):
        with pytest.raises(Exception) as exc:
            banking_tools.get_customer_info("C9999")
        assert "customer_not_found" in str(exc.value)