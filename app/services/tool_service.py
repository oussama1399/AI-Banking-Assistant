"""
Tool Service — thin wrapper around the 5 banking tools.

Centralizes parameter passing, error normalization, and observability.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from app.monitoring.metrics import TOOL_CALLS_TOTAL, TOOL_LATENCY
from app.tools import banking_tools

logger = logging.getLogger(__name__)


# Mapping of tool names → underlying functions.
TOOL_REGISTRY = {
    "get_account_balance": banking_tools.get_account_balance,
    "get_transactions": banking_tools.get_transactions,
    "get_card_info": banking_tools.get_card_info,
    "get_transfer_status": banking_tools.get_transfer_status,
    "get_customer_info": banking_tools.get_customer_info,
}


class ToolServiceError(Exception):
    """Normalized error returned by the ToolService."""

    def __init__(self, kind: str, message: str = "") -> None:
        self.kind = kind
        self.message = message or kind
        super().__init__(self.message)


class ToolService:
    """Resolves tool names to invocations and normalizes errors."""

    def call(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        if tool_name not in TOOL_REGISTRY:
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="unknown_tool").inc()
            raise ToolServiceError(
                "unknown_tool",
                f"Outil inconnu: {tool_name}",
            )

        func = TOOL_REGISTRY[tool_name]
        t0 = time.perf_counter()
        try:
            result = func(**parameters)
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="success").inc()
            return result
        except Exception as e:
            err_text = str(e)
            # Normalize the most common errors.
            if "customer_not_found" in err_text:
                TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="customer_not_found").inc()
                raise ToolServiceError("customer_not_found", str(e)) from e
            if "transfer_not_found" in err_text:
                TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="transfer_not_found").inc()
                raise ToolServiceError("transfer_not_found", str(e)) from e
            if isinstance(e, FileNotFoundError):
                TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="data_unavailable").inc()
                raise ToolServiceError("data_unavailable", str(e)) from e
            logger.exception("Tool %s failed: %s", tool_name, e)
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status="error").inc()
            raise ToolServiceError("tool_error", str(e)) from e
        finally:
            elapsed = time.perf_counter() - t0
            TOOL_LATENCY.labels(tool_name=tool_name).observe(elapsed)


_default_tool_service: Optional[ToolService] = None


def get_default_tool_service() -> ToolService:
    global _default_tool_service
    if _default_tool_service is None:
        _default_tool_service = ToolService()
    return _default_tool_service
