"""
Router for the AI Banking Assistant.

Decides whether a user message should be answered by:
  - a single banking tool,
  - the RAG knowledge base,
  - a combination of tool + RAG,
  - or a clarification request (missing required parameter).

Strategy: hybrid rule-based (regex + keyword heuristics). Fast, deterministic,
predictable, no LLM call needed for routing. An LLM-based fallback router can
replace or complement this later.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# --- Patterns ---------------------------------------------------------------

# Transfer IDs: "TR4587", "TR 4587", "tr-4587"
TRANSFER_ID_RE = re.compile(r"\bTR[- ]?\d{2,}\b", re.IGNORECASE)

# Date ranges used to filter transactions.
# Capture phrases like "du 1er août 2026 au 15 août 2026" or "entre X et Y".
DATE_FR_RE = re.compile(
    r"\b(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})\b"
)

# --- Keyword groups ---------------------------------------------------------

# Phrases that strongly imply "explain the procedure / reason":
# Tool + RAG trigger.
PROCEDURE_TRIGGERS: Set[str] = {
    "pourquoi", "que faire", "que dois-je faire", "que dois je faire",
    "comment faire", "comment reessayer", "comment réessayer",
    "comment proceder", "comment procéder", "que se passe",
    "que dois-je", "marche a faire", "marche à faire",
    "quoi faire", "refuse", "refusé", "rejete", "rejeté", "rejected",
    "explique", "expliquez", "explication",
}

# Money / General info triggers (often imply RAG when paired with transfer or card)
GENERAL_INFO_TRIGGERS: Set[str] = {
    "frais", "tarif", "tarifs", "coute", "coûte", "combien coute", "combien coûte",
    "international", "internationaux", "delai", "délai", "délais", "delais",
    "politique", "conditions", "condition", "regle", "règle", "regles", "règles",
    "documents", "document", "justificatif", "limite", "plafond",
}

# Money-related verbs that need RAG context (procedure / rules).
_MONEY_RAG_TRIGGERS: Set[str] = {
    "combien", "montant max", "plafond", "limite",
    "frais", "coute", "coûte", "tarif",
    "combien coute", "combien coûte",
}

# Personal-account keywords (Tool only).
BALANCE_KEYWORDS: Set[str] = {"solde", "balance", "combien j ai", "combien j'ai"}
TRANSACTIONS_KEYWORDS: Set[str] = {
    "transactions", "transaction", "operations", "opérations",
    "paiements", "paiement", "historique", "mouvements",
    "dernieres operations", "dernières opérations",
    "depenses", "dépenses",
}
CARD_KEYWORDS: Set[str] = {
    "carte", "cb", "visa", "mastercard",
    "ma carte",
}
CUSTOMER_KEYWORDS: Set[str] = {
    "mon profil", "mes informations", "mes infos",
    "qui suis-je", "qui suis je", "ma fiche",
    "informations personnelles", "donnees personnelles",
    "données personnelles",
}

# General-question keywords (RAG only).
RAG_KEYWORDS: Set[str] = {
    "comment ouvrir", "ouvrir un compte", "ouverture de compte",
    "que faire en cas", "que faire si",
    "carte perdue", "carte volee", "carte volée",
    "perte de carte", "vol de carte", "perte", "vol",
    "politique", "conditions", "procedure", "procédure",
    "documents necessaires", "documents nécessaires",
    "pret immobilier", "prêt immobilier",
    "pret a la consommation", "prêt à la consommation",
    "fraude",
}


# --- Data structures --------------------------------------------------------

ROUTE_TYPES = ("tool", "rag", "tool+rag", "clarification")


@dataclass
class RouteDecision:
    """Output of the router: what to call, with which parameters."""

    route_type: str  # one of ROUTE_TYPES
    tool: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    needs_rag: bool = False
    missing_parameter: Optional[str] = None
    reason: str = ""

    @property
    def is_clarification(self) -> bool:
        return self.route_type == "clarification"

    @property
    def is_tool(self) -> bool:
        return self.route_type in ("tool", "tool+rag") and self.tool is not None


# --- Helper ----------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase + strip + collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def _has_any(text: str, keywords: Set[str]) -> bool:
    """True if `text` (lowercased) contains any of the given substrings."""
    norm = _normalize(text)
    for kw in keywords:
        if kw in norm:
            return True
    return False


def _extract_transfer_id(text: str) -> Optional[str]:
    m = TRANSFER_ID_RE.search(text)
    if not m:
        return None
    return re.sub(r"[- ]", "", m.group(0)).upper()


def _extract_dates(text: str) -> Dict[str, Optional[str]]:
    """Best-effort extraction of start/end dates from a French query."""
    matches = DATE_FR_RE.findall(text)
    out: Dict[str, Optional[str]] = {"start_date": None, "end_date": None}
    if len(matches) >= 1:
        out["start_date"] = matches[0]
    if len(matches) >= 2:
        out["end_date"] = matches[1]
    return out


def _wants_procedure(text: str) -> bool:
    return _has_any(text, PROCEDURE_TRIGGERS)


# --- Main router ------------------------------------------------------------

class BankingRouter:
    """Rule-based router for banking queries.

    Public API: ``classify(customer_id, message) -> RouteDecision``.
    """

    # Keyword groups exposed for testing.
    ALL_KEYWORDS = {
        "balance": BALANCE_KEYWORDS,
        "transactions": TRANSACTIONS_KEYWORDS,
        "card": CARD_KEYWORDS,
        "customer": CUSTOMER_KEYWORDS,
        "rag": RAG_KEYWORDS,
        "procedure": PROCEDURE_TRIGGERS,
    }

    def classify(self, customer_id: str, message: str) -> RouteDecision:
        """Analyze the user message and return a routing decision."""
        logger.debug("Routing classify request - customer_id: %s, message: '%s'", customer_id, message)

        if not message or not message.strip():
            logger.info("Routing decision: clarification (empty message)")
            return RouteDecision(
                route_type="clarification",
                missing_parameter="message",
                reason="Le message est vide.",
            )

        transfer_id = _extract_transfer_id(message)
        wants_procedure = _wants_procedure(message)
        is_general_info = _has_any(message, GENERAL_INFO_TRIGGERS) or _has_any(message, RAG_KEYWORDS)

        # --- Explicit RAG keywords (e.g. perte de carte, ouverture de compte, etc.) ---
        if _has_any(message, RAG_KEYWORDS) and transfer_id is None and not _has_any(message, {"statut de ma carte", "statut de mon virement", "statut de mon compte"}):
            logger.info("Routing decision: RAG (matched RAG_KEYWORDS) for message: '%s'", message)
            return RouteDecision(
                route_type="rag",
                tool=None,
                parameters={"customer_id": customer_id, "query": message},
                needs_rag=True,
                reason="Demande d'information générale ou procédure RAG.",
            )

        # --- Transfer (most specific path) -------------------------------
        if _has_any(message, {"virement", "virements", "transfert", "transferts", "transfer"}) or transfer_id is not None:
            if transfer_id is None:
                if is_general_info and not _has_any(message, {"mon virement", "statut", "suivi", "etat", "état"}):
                    logger.info("Routing decision: RAG (general transfer inquiry) for message: '%s'", message)
                    return RouteDecision(
                        route_type="rag",
                        tool=None,
                        parameters={"customer_id": customer_id, "query": message},
                        needs_rag=True,
                        reason="Demande d'information générale sur les virements.",
                    )
                logger.info("Routing decision: clarification (missing transfer_id) for message: '%s'", message)
                return RouteDecision(
                    route_type="clarification",
                    tool="get_transfer_status",
                    parameters={"transfer_id": None, "customer_id": customer_id},
                    missing_parameter="transfer_id",
                    reason="Un identifiant de virement (ex: TR4587) est requis.",
                )

            decision = RouteDecision(
                route_type="tool+rag" if wants_procedure else "tool",
                tool="get_transfer_status",
                parameters={"transfer_id": transfer_id},
                needs_rag=wants_procedure,
                reason=(
                    "Le client demande pourquoi / que faire → tool + RAG"
                    if wants_procedure
                    else "Le client demande le statut d'un virement → tool seul."
                ),
            )
            logger.info("Routing decision: %s (transfer_id=%s)", decision.route_type, transfer_id)
            return decision

        # --- Balance ------------------------------------------------------
        if _has_any(message, BALANCE_KEYWORDS):
            logger.info("Routing decision: tool get_account_balance for customer_id: %s", customer_id)
            return RouteDecision(
                route_type="tool",
                tool="get_account_balance",
                parameters={"customer_id": customer_id},
                needs_rag=False,
                reason="Le client demande son solde → outil get_account_balance.",
            )

        # --- Transactions -------------------------------------------------
        if _has_any(message, TRANSACTIONS_KEYWORDS):
            dates = _extract_dates(message)
            params: Dict[str, Any] = {"customer_id": customer_id}
            params.update(dates)
            logger.info("Routing decision: tool get_transactions for customer_id: %s", customer_id)
            return RouteDecision(
                route_type="tool",
                tool="get_transactions",
                parameters=params,
                needs_rag=False,
                reason="Le client demande son historique → outil get_transactions.",
            )

        # --- Card info ----------------------------------------------------
        if _has_any(message, CARD_KEYWORDS):
            wants_rag = any(k in _normalize(message) for k in _MONEY_RAG_TRIGGERS)
            decision = RouteDecision(
                route_type="tool+rag" if wants_rag else "tool",
                tool="get_card_info",
                parameters={"customer_id": customer_id},
                needs_rag=wants_rag,
                reason=(
                    "Le client mélange carte + règles → tool + RAG."
                    if wants_rag
                    else "Le client demande des infos sur sa carte → outil get_card_info."
                ),
            )
            logger.info("Routing decision: %s for card_info", decision.route_type)
            return decision

        # --- Customer profile --------------------------------------------
        if _has_any(message, CUSTOMER_KEYWORDS):
            logger.info("Routing decision: tool get_customer_info for customer_id: %s", customer_id)
            return RouteDecision(
                route_type="tool",
                tool="get_customer_info",
                parameters={"customer_id": customer_id},
                needs_rag=False,
                reason="Le client demande ses informations → outil get_customer_info.",
            )

        # --- Default: RAG-only --------------------------------------------
        logger.info("Routing decision: RAG default for message: '%s'", message)
        return RouteDecision(
            route_type="rag",
            tool=None,
            parameters={"customer_id": customer_id, "query": message},
            needs_rag=True,
            reason="Aucune correspondance tool → RAG général.",
        )


# --- Convenience singleton ---------------------------------------------------

_default_router: Optional[BankingRouter] = None


def get_default_router() -> BankingRouter:
    global _default_router
    if _default_router is None:
        _default_router = BankingRouter()
    return _default_router

