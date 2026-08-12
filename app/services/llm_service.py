"""
LLM service wrapping Ollama for the AI Banking Assistant.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore

from app.services.prompts import (
    RAG_ONLY_PROMPT,
    SYSTEM_PROMPT,
    TOOL_ONLY_PROMPT,
    TOOL_RAG_PROMPT,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when the LLM cannot be reached or is misconfigured."""


class OllamaLLMService:
    """Wrapper around Ollama for banking response generation."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "qwen3-coder:30b",
        temperature: float = 0.1,
        max_output_tokens: int = 1024,
    ) -> None:
        self.host = host
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        # Check if Ollama is available
        self._ollama_available = self._check_ollama()

        logger.info("OllamaLLMService initialized with model=%s, host=%s", model, host)

    def _check_ollama(self) -> bool:
        """Check if Ollama service is available."""
        try:
            if httpx is None:
                return False
            response = httpx.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            logger.warning("Ollama service not available at %s", self.host)
            return False

    # --- Public API --------------------------------------------------------

    def answer_with_tool(
        self,
        message: str,
        tool_result: Dict[str, Any],
        tool_name: str,
    ) -> str:
        """Generate a response using only a tool result."""
        if not self._ollama_available:
            return self._fallback_tool(message, tool_result, tool_name)

        prompt = TOOL_ONLY_PROMPT.format(
            system=SYSTEM_PROMPT,
            message=message,
            tool_name=tool_name,
            tool_result=json.dumps(tool_result, ensure_ascii=False, indent=2),
        )
        return self._generate(prompt)

    def answer_with_rag(
        self,
        message: str,
        documents: List[Dict[str, Any]],
    ) -> str:
        """Generate a response using only RAG documents."""
        if not self._ollama_available:
            return self._fallback_rag(message, documents)

        formatted_docs = self._format_documents(documents)
        prompt = RAG_ONLY_PROMPT.format(
            system=SYSTEM_PROMPT,
            message=message,
            documents=formatted_docs,
        )
        return self._generate(prompt)

    def answer_with_tool_and_rag(
        self,
        message: str,
        tool_result: Dict[str, Any],
        tool_name: str,
        documents: List[Dict[str, Any]],
    ) -> str:
        """Generate a response combining a tool result and RAG documents."""
        if not self._ollama_available:
            return self._fallback_tool_rag(message, tool_result, tool_name, documents)

        formatted_docs = self._format_documents(documents)
        prompt = TOOL_RAG_PROMPT.format(
            system=SYSTEM_PROMPT,
            message=message,
            tool_name=tool_name,
            tool_result=json.dumps(tool_result, ensure_ascii=False, indent=2),
            documents=formatted_docs,
        )
        return self._generate(prompt)

    # --- Internals ---------------------------------------------------------

    def _generate(self, prompt: str) -> str:
        """Generate response using Ollama API."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_output_tokens
                }
            }

            response = httpx.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                if not text:
                    raise Exception("Empty response from Ollama")
                return text
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.exception("Ollama call failed: %s", e)
            # Fall back to simple response when Ollama fails
            return f"(Ollama unavailable) Error: {e}"

    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        blocks: List[str] = []
        for i, doc in enumerate(documents, start=1):
            source = doc.get("metadata", {}).get("source", "unknown")
            content = doc.get("content", "")
            blocks.append(f"[Doc {i} — {source}]\n{content}")
        return "\n\n".join(blocks) if blocks else "(aucun document)"

    # --- Fallbacks ---------------------------------------------------------

    @staticmethod
    def _fallback_tool(message: str, tool_result: Dict[str, Any], tool_name: str) -> str:
        return (
            f"(Ollama fallback mode)\n"
            f"Question : {message}\n"
            f"Résultat de l'outil `{tool_name}` : "
            f"{json.dumps(tool_result, ensure_ascii=False, indent=2)}"
        )

    @staticmethod
    def _fallback_rag(message: str, documents: List[Dict[str, Any]]) -> str:
        if not documents:
            return (
                "(Ollama fallback mode) Aucun document pertinent trouvé pour : "
                f"{message}"
            )
        best = documents[0]
        source = best.get("metadata", {}).get("source", "documentation")
        return (
            f"(Ollama fallback mode)\n"
            f"Question : {message}\n"
            f"Source : {source}\n{best.get('content', '')[:600]}"
        )

    @staticmethod
    def _fallback_tool_rag(
        message: str,
        tool_result: Dict[str, Any],
        tool_name: str,
        documents: List[Dict[str, Any]],
    ) -> str:
        tool_part = json.dumps(tool_result, ensure_ascii=False, indent=2)
        doc_part = documents[0].get("content", "")[:400] if documents else ""
        return (
            f"(Ollama fallback mode)\n"
            f"Question : {message}\n\n"
            f"Étapes :\n"
            f"1. Situation personnelle (outil `{tool_name}`) : {tool_part}\n"
            f"2. Règle générale (RAG) : {doc_part}"
        )


# --- Convenience singleton --------------------------------------------------

_default_llm: Optional[OllamaLLMService] = None


def get_default_llm() -> OllamaLLMService:
    global _default_llm
    if _default_llm is None:
        _default_llm = OllamaLLMService()
    return _default_llm