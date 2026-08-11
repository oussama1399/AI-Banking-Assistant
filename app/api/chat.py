"""
Chat API router for AI Banking Assistant
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models.chat import ChatRequest, ChatResponse
from app.services.orchestrator import BankingOrchestrator

router = APIRouter()

# Initialize the orchestrator once
orchestrator = BankingOrchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for banking assistant
    """
    try:
        response = await orchestrator.handle_chat(
            customer_id=request.customer_id,
            message=request.message
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}