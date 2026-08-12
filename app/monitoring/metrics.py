"""
Prometheus metrics collection module for AI Banking Assistant.
"""

from prometheus_client import Counter, Histogram

# --- Chat Endpoint Metrics ----------------------------------------------------

CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "Total chat requests handled by the assistant",
    ["route_type", "status"],
)

CHAT_REQUEST_LATENCY = Histogram(
    "chat_request_latency_seconds",
    "Latency of /chat request processing in seconds",
    ["route_type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# --- Tool Execution Metrics ---------------------------------------------------

TOOL_CALLS_TOTAL = Counter(
    "tool_calls_total",
    "Total executions of banking tools",
    ["tool_name", "status"],
)

TOOL_LATENCY = Histogram(
    "tool_latency_seconds",
    "Latency of banking tool executions in seconds",
    ["tool_name"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0),
)

# --- RAG Search Metrics -------------------------------------------------------

RAG_QUERIES_TOTAL = Counter(
    "rag_queries_total",
    "Total RAG search queries executed",
    ["status"],
)

RAG_LATENCY = Histogram(
    "rag_latency_seconds",
    "Latency of RAG document retrieval in seconds",
    buckets=(0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# --- Error Metrics ------------------------------------------------------------

ERRORS_TOTAL = Counter(
    "errors_total",
    "Total application errors by error type",
    ["error_type"],
)
