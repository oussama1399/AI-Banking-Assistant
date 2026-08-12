import logging
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.orchestrator import BankingOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy-initialized orchestrator (heavy RAG/LLM init deferred).
_orchestrator: BankingOrchestrator | None = None


def get_orchestrator() -> BankingOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BankingOrchestrator()
    return _orchestrator


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint for the banking assistant."""
    logger.info("Received POST /chat request from customer_id=%s, message_len=%d", request.customer_id, len(request.message))
    try:
        response = await get_orchestrator().handle_chat(
            customer_id=request.customer_id,
            message=request.message,
        )
        logger.info("POST /chat completed for customer_id=%s, source=%s", request.customer_id, response.source)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in /chat endpoint for customer_id=%s: %s", request.customer_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

