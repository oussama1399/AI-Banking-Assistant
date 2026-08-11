# AI Banking Assistant - Architecture

## Overview

This is a comprehensive AI Banking Assistant project that implements an intelligent chatbot system capable of handling customer banking inquiries through a single API endpoint `/chat`. The system intelligently routes questions between Retrieval-Augmented Generation (RAG) for general banking information and tools/APIs for specific customer data.

## Architecture Diagram

```mermaid
graph TD
    A[User/Client] --> B[FastAPI Endpoint /chat]
    
    B --> C[Orchestrator]
    
    C --> D[Router]
    C --> E[Tool Service]
    C --> F[RAG Service]
    C --> G[LLM Service]
    C --> H[Monitoring & Observability]
    
    D -->|RAG-only| F
    D -->|Tool-only| E
    D -->|Tool+RAG| E
    D -->|Tool+RAG| F
    
    E --> H1[get_account_balance]
    E --> H2[get_transactions]
    E --> H3[get_card_info]
    E --> H4[get_transfer_status]
    E --> H5[get_customer_info]
    
    F --> M[ChromaDB Vector Store]
    F --> N[Text Splitter]
    F --> O[Embeddings Model]
    F --> P[RAG Pipeline]
    
    G --> Q[LLM Model]
    G --> R[Response Generator]
    
    H --> S[Prometheus Metrics]
    H --> T[Grafana Dashboards]
    H --> U[RAGAS Evaluation]
    
    M --> P
    N --> P
    O --> P
    
    P --> Q
    Q --> R
    
    R --> B
    S --> V[Prometheus Server]
    T --> W[Grafana Server]
    U --> X[RAGAS Framework]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bfb,stroke:#333
    style D fill:#fbb,stroke:#333
    style E fill:#bfb,stroke:#333
    style F fill:#bfb,stroke:#333
    style G fill:#bfb,stroke:#333
    style H fill:#f9f,stroke:#333
    style H1 fill:#ff9,stroke:#333
    style H2 fill:#ff9,stroke:#333
    style H3 fill:#ff9,stroke:#333
    style H4 fill:#ff9,stroke:#333
    style H5 fill:#ff9,stroke:#333
    style M fill:#9ff,stroke:#333
    style N fill:#9ff,stroke:#333
    style O fill:#9ff,stroke:#333
    style P fill:#9ff,stroke:#333
    style Q fill:#9f9,stroke:#333
    style R fill:#9f9,stroke:#333
    style S fill:#f99,stroke:#333
    style T fill:#f99,stroke:#333
    style U fill:#f99,stroke:#333
    style V fill:#ff9,stroke:#333
    style W fill:#ff9,stroke:#333
    style X fill:#ff9,stroke:#333
```

## Components Description

### 1. User/Client
- The external interface that sends requests to the banking assistant

### 2. FastAPI Endpoint (/chat)
- Main API endpoint for receiving chat requests
- Handles request validation and response formatting
- Routes requests to the orchestrator
- Exposes `/metrics` endpoint for Prometheus scraping

### 3. Orchestrator
- Core component that coordinates between different services
- Determines which data sources to use based on the query
- Integrates results from tools and RAG when needed

### 4. Router
- Analyzes user queries to determine appropriate data source
- Routes to:
  - RAG-only queries (general banking questions)
  - Tool-only queries (personal account information)
  - Tool + RAG queries (complex questions requiring both)

### 5. Tool Service
- Contains 5 banking API functions:
  - `get_account_balance(customer_id)`
  - `get_transactions(customer_id, start_date=None, end_date=None)`
  - `get_card_info(customer_id)`
  - `get_transfer_status(transfer_id)`
  - `get_customer_info(customer_id)`

### 6. RAG Service
- Retrieves relevant documents from knowledge base
- Uses ChromaDB vector store for document retrieval
- Processes text with embeddings and similarity search
- Provides context to LLM for answer generation

### 7. LLM Service
- Generates final responses based on retrieved information
- Uses appropriate prompts for different response types
- Ensures no invented information in responses

### 8. Monitoring & Observability
- **Prometheus**: Collects and stores time-series metrics
- **Grafana**: Visualizes metrics through dashboards and alerting
- **RAGAS**: Evaluates RAG quality (faithfulness, relevancy, precision)

## Data Flow

1. User sends request to `/chat` endpoint with `customer_id` and `message`
2. Orchestrator receives the request and passes it to Router
3. Router analyzes query and determines data source(s):
   - RAG-only: Query about general banking procedures → use only RAG
   - Tool-only: Query about personal account information → use only tools  
   - Tool + RAG: Complex query requiring both → use both
4. Based on routing decision:
   - If RAG-only: Query RAG service for relevant documents
   - If Tool-only: Query appropriate tool(s) with customer ID
   - If Tool + RAG: Query both tools and RAG, then combine results
5. Results are passed to LLM service for response generation
6. Final response is returned to user with source information
7. Metrics are collected and sent to Prometheus for monitoring
8. Grafana dashboards visualize the metrics and alert on issues
9. RAGAS evaluates quality of responses and RAG performance

## Monitoring Components

### Prometheus Metrics Collection
- Request counts by route type (RAG-only, Tool-only, Tool+RAG)
- Latency measurements for requests, tools, and RAG
- Tool call success/failure rates
- Cache hit/miss ratios
- Fact checking results
- RAG quality scores (faithfulness, relevancy, precision)

### Grafana Dashboards
1. **Banking Assistant Overview**: Request rates, error rates, latency by route type
2. **RAG Quality**: RAGAS evaluation scores and trends
3. **Tools & Errors**: Tool call statistics, error rates, cache performance

### RAGAS Evaluation
- Offline evaluation on test datasets
- Online sampling of production requests for quality assessment
- Metrics: faithfulness, answer relevancy, context precision, etc.