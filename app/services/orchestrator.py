"""
Banking Assistant Orchestrator.

Routes user queries to the appropriate data source (RAG, tool, or both),
collects the context, and asks the LLM to produce a final natural-language
response. Handles errors and missing parameters gracefully.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from app.models.chat import ChatRequest, ChatResponse
from app.monitoring.metrics import (
    CHAT_REQUEST_LATENCY,
    CHAT_REQUESTS_TOTAL,
    ERRORS_TOTAL,
)
from app.services.llm_service import get_default_llm, LLMUnavailableError
from app.services.rag_service import RAGService
from app.services.router import BankingRouter, RouteDecision
from app.services.tool_service import ToolService, ToolServiceError

logger = logging.getLogger(__name__)


# User-facing error messages (FR).
_ERROR_MESSAGES = {
    "customer_not_found": (
        "Je n'ai trouvé aucun compte associé à cet identifiant client. "
        "Merci de vérifier l'identifiant."
    ),
    "transfer_not_found": (
        "Aucun virement avec cet identifiant n'a été trouvé. "
        "Merci de vérifier le numéro de virement (ex: TR4587)."
    ),
    "data_unavailable": (
        "Je ne peux pas accéder à vos données pour le moment. "
        "Veuillez réessayer plus tard."
    ),
    "tool_error": (
        "Une erreur technique est survenue. Veuillez réessayer plus tard."
    ),
    "unknown_tool": "Outil interne inconnu — contactez le support.",
    "service_unavailable": (
        "Le service est momentanément indisponible. Veuillez réessayer."
    ),
    "llm_unavailable": (
        "Le service de génération de réponse est momentanément indisponible. "
        "Voici les informations brutes : {raw}"
    ),
}


class BankingOrchestrator:
    """Coordinates Router, ToolService, RAGService, and LLMService."""

    def __init__(
        self,
        router: Optional[BankingRouter] = None,
        tool_service: Optional[ToolService] = None,
        rag_service: Optional[RAGService] = None,
        llm_service: Optional[LLMService] = None,
    ) -> None:
        self.router = router or BankingRouter()
        self.tool_service = tool_service or ToolService()
        self.rag_service = rag_service or RAGService()
        self.llm_service = llm_service or get_default_llm()

    # --- Main entrypoint --------------------------------------------------

    async def handle_chat(
        self,
        customer_id: str,
        message: str,
    ) -> ChatResponse:
        """Handle a /chat request and return a structured ChatResponse."""
        t0 = time.perf_counter()
        route_type_for_metrics = "unknown"
        logger.info("Starting handle_chat - customer_id: %s, message: '%s'", customer_id, message)
        try:
            # 1. Routing decision.
            route: RouteDecision = self.router.classify(customer_id, message)
            route_type_for_metrics = route.route_type
            logger.info("Orchestrator route decision: type=%s, tool=%s, needs_rag=%s, missing=%s",
                        route.route_type, route.tool, route.needs_rag, route.missing_parameter)

            # 2. Clarification if a required parameter is missing.
            if route.is_clarification:
                answer = self._clarification_message(route)
                logger.info("Returning clarification response for missing parameter: %s", route.missing_parameter)
                CHAT_REQUESTS_TOTAL.labels(route_type="clarification", status="success").inc()
                return ChatResponse(answer=answer, source="clarification")

            # 3. Tool execution (if any).
            tool_result: Optional[Dict[str, Any]] = None
            tool_name: Optional[str] = None
            if route.is_tool:
                tool_name = route.tool
                logger.info("Calling tool %s with params: %s", tool_name, route.parameters)
                try:
                    tool_result = self.tool_service.call(
                        tool_name, route.parameters
                    )
                    logger.debug("Tool %s executed successfully", tool_name)
                except ToolServiceError as e:
                    logger.warning("ToolServiceError in %s: %s (kind=%s)", tool_name, e.message, e.kind)
                    CHAT_REQUESTS_TOTAL.labels(route_type=route_type_for_metrics, status="tool_error").inc()
                    ERRORS_TOTAL.labels(error_type=e.kind).inc()
                    return ChatResponse(
                        answer=_ERROR_MESSAGES.get(
                            e.kind, f"Erreur: {e.message}"
                        ),
                        source="error",
                    )

            # 4. RAG retrieval (if needed).
            documents: List[Dict[str, Any]] = []
            if route.needs_rag:
                rag_query = self._build_rag_query(message, tool_result)
                logger.info("Searching RAG knowledge base with query: '%s'", rag_query)
                documents = self.rag_service.search(rag_query)
                logger.info("RAG search returned %d relevant documents", len(documents))

            # 5. LLM final response generation.
            source = self._build_source(tool_name, route.needs_rag)
            docs_for_response = [
                d.get("metadata", {}).get("source", "")
                for d in documents
                if d.get("metadata", {}).get("source")
            ]

            try:
                logger.debug("Generating LLM response for source=%s", source)
                answer = self._generate_answer(
                    message=message,
                    route=route,
                    tool_result=tool_result,
                    tool_name=tool_name,
                    documents=documents,
                )
            except LLMUnavailableError as e:
                logger.warning("LLM unavailable, using fallback: %s", e)
                ERRORS_TOTAL.labels(error_type="llm_unavailable").inc()
                raw = json.dumps(
                    {"tool": tool_result, "docs": [d.get("content", "")[:200] for d in documents]},
                    ensure_ascii=False,
                )
                answer = _ERROR_MESSAGES["llm_unavailable"].format(raw=raw)

            CHAT_REQUESTS_TOTAL.labels(route_type=route_type_for_metrics, status="success").inc()
            return ChatResponse(
                answer=answer,
                source=source,
                documents=docs_for_response or None,
            )

        except Exception as e:
            logger.exception("Unhandled error in orchestrator: %s", e)
            CHAT_REQUESTS_TOTAL.labels(route_type=route_type_for_metrics, status="error").inc()
            ERRORS_TOTAL.labels(error_type="unhandled_orchestrator_error").inc()
            return ChatResponse(
                answer=_ERROR_MESSAGES["service_unavailable"],
                source="error",
            )
        finally:
            elapsed_sec = time.perf_counter() - t0
            CHAT_REQUEST_LATENCY.labels(route_type=route_type_for_metrics).observe(elapsed_sec)
            logger.info("Chat handling completed in %.1f ms", elapsed_sec * 1000)

    # --- Helpers ----------------------------------------------------------

    @staticmethod
    def _clarification_message(route: RouteDecision) -> str:
        if route.missing_parameter == "transfer_id":
            return (
                "Pour consulter le statut d'un virement, merci de me "
                "communiquer son identifiant (ex: TR4587)."
            )
        if route.missing_parameter == "message":
            return "Merci de poser une question."
        if route.missing_parameter == "customer_id":
            return "Merci de fournir un identifiant client."
        return (
            "Merci de reformuler votre question ou de préciser les "
            "informations manquantes."
        )

    @staticmethod
    def _build_source(tool_name: Optional[str], needs_rag: bool) -> str:
        if tool_name and needs_rag:
            return f"{tool_name}+RAG"
        if tool_name:
            return tool_name
        return "RAG"

    @staticmethod
    def _build_rag_query(
        message: str, tool_result: Optional[Dict[str, Any]]
    ) -> str:
        """Combine the user message with a hint from the tool result
        to retrieve the most relevant doc chunks."""
        if not tool_result:
            return message
        # Add a hint from the tool result so the retriever picks the
        # right policy document.
        hint_parts: List[str] = []
        for key in ("status", "reason", "card_type", "account_type"):
            if key in tool_result and tool_result[key]:
                hint_parts.append(str(tool_result[key]))
        if hint_parts:
            return f"{message} — contexte: {', '.join(hint_parts)}"
        return message

    def _generate_answer(
        self,
        message: str,
        route: RouteDecision,
        tool_result: Optional[Dict[str, Any]],
        tool_name: Optional[str],
        documents: List[Dict[str, Any]],
    ) -> str:
        if tool_name and route.needs_rag:
            return self.llm_service.answer_with_tool_and_rag(
                message=message,
                tool_result=tool_result,
                tool_name=tool_name,
                documents=documents,
            )
        if tool_name:
            return self.llm_service.answer_with_tool(
                message=message,
                tool_result=tool_result,
                tool_name=tool_name,
            )
        return self.llm_service.answer_with_rag(
            message=message,
            documents=documents,
        )


# --- Convenience singleton --------------------------------------------------

_default_orchestrator: Optional[BankingOrchestrator] = None


def get_default_orchestrator() -> BankingOrchestrator:
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = BankingOrchestrator()
    return _default_orchestrator
