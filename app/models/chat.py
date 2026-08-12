"""
Data models for AI Banking Assistant
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    customer_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    source: str
    documents: Optional[List[str]] = None


class ToolRoute(BaseModel):
    tool: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    needs_rag: bool = False
    reason: str = ""


class TransferStatusResponse(BaseModel):
    transfer_id: str
    amount: float
    beneficiary: str
    date: str
    status: str
    reason: Optional[str] = None


class AccountBalanceResponse(BaseModel):
    customer_id: str
    available_balance: float
    currency: str
    account_type: str


class CardInfoResponse(BaseModel):
    customer_id: str
    card_type: str
    status: str
    expiration_date: str
    payment_limit: float
    used_amount: float


class CustomerInfoResponse(BaseModel):
    customer_id: str
    name: str
    account_status: str
    risk_profile: str


class TransactionResponse(BaseModel):
    transaction_id: str
    date: str
    label: str
    amount: float
    currency: str
