"""
Banking Assistant Orchestrator
This will handle routing between RAG, tools, and combining both when needed
"""

from typing import Dict, Any, Optional
from app.models.chat import ChatRequest, ChatResponse

class BankingOrchestrator:
    """
    Main orchestrator that routes queries to appropriate sources
    """

    def __init__(self):
        # Initialize components here
        pass

    async def handle_chat(self, customer_id: str, message: str) -> ChatResponse:
        """
        Main method to handle chat requests
        """
        # This will be implemented in later phases
        raise NotImplementedError("Orchestrator not yet implemented")