# AI Banking Assistant Project

## Project Overview

This is a comprehensive AI Banking Assistant project that implements an intelligent chatbot system capable of handling customer banking inquiries through a single API endpoint `/chat`. The system intelligently routes questions between Retrieval-Augmented Generation (RAG) for general banking information and tools/APIs for specific customer data.

## Key Features

### API Endpoint
- `POST /chat` accepting:
  ```json
  {
    "customer_id": "C1024",
    "message": "Quel est le statut de mon virement TR4587 ?"
  }
  ```
- Returns structured responses with answer and source information

### Banking Tools (5 mocked services)
1. `get_account_balance(customer_id)`
2. `get_transactions(customer_id, start_date=None, end_date=None)`
3. `get_card_info(customer_id)`
4. `get_transfer_status(transfer_id)`
5. `get_customer_info(customer_id)`

### RAG Knowledge Base
- Documents covering various banking topics:
  - Account fees and opening
  - Card limits and policies  
  - Fraud policy
  - International transfers
  - Loan information
  - Lost card procedures
  - Transfer policies

### Routing System
The system intelligently routes questions:
- **RAG-only**: General questions about banking procedures
- **Tool-only**: Personal account inquiries 
- **Tool + RAG**: Complex questions requiring both personal data and general knowledge

### Monitoring & Observability
- Prometheus integration for real-time metrics collection
- Grafana dashboards for visualization and alerting
- RAGAS evaluation for quality assessment of RAG performance
- Comprehensive monitoring of:
  - Request rates and latencies
  - Tool call success/failure rates
  - Cache hit ratios
  - Fact checking results
  - RAG quality scores (faithfulness, relevancy, precision)

## Implementation Approach

1. Setup & Mock Tools - Create the basic project structure with 5 mocked banking APIs
2. RAG Pipeline - Build document processing, chunking, embeddings, and vector store
3. Router - Implement intelligent routing logic between RAG and tools
4. API Integration - Connect everything into a complete FastAPI endpoint
5. Error Handling - Robust error management for missing data, invalid requests, etc.
6. Monitoring & Observability - Implement Prometheus, Grafana, and RAGAS integration
7. Testing - Comprehensive test coverage of all components
8. Documentation - Complete README with usage examples

## Current Progress

### Phase 1: Project Setup Completed
- Created complete project directory structure
- Implemented FastAPI application framework with proper routing
- Set up configuration management
- Created data models for API requests and responses
- Established testing framework
- All dependencies installed via requirements.txt

### Phase 2: Mock Banking Tools Implemented
- Implemented `get_account_balance(customer_id)` function
- Implemented `get_transactions(customer_id, start_date=None, end_date=None)` function  
- Implemented `get_card_info(customer_id)` function
- Implemented `get_transfer_status(transfer_id)` function
- Implemented `get_customer_info(customer_id)` function
- All functions properly connect to CSV data files in the data/ directory
- Added comprehensive error handling for missing data
- Created test suite to verify all tools work correctly

### Phase 3: RAG Knowledge Base Implemented
- Created complete banking documentation in markdown format (knowledge_base/)
- Implemented RAG pipeline using LangChain and ChromaDB
- Documents include: card policies, transfer policies, account fees, etc.
- Added text splitting with appropriate chunk size (500 characters)
- Integrated sentence transformers for embeddings
- Setup document retrieval and QA chain
- Created test functions to verify RAG functionality

### Phase 4: Routing System Implemented
- Implemented intelligent routing logic between RAG and tools
- Created logic for identifying when to use:
  - RAG-only queries (general banking questions)
  - Tool-only queries (personal account information)
  - Tool + RAG queries (complex questions requiring both)
- Added parameter extraction from user messages
- Added validation for missing parameters

### Phase 5: API Integration Completed
- Created the main `/chat` endpoint with proper request/response models
- Implemented input validation using Pydantic models
- Integrated all components (router, tools, RAG, LLM)
- Added health check endpoint (`/health`)
- Configured proper HTTP status codes and error responses

### Phase 6: Monitoring & Observability Implemented
- Integrated Prometheus client for custom metrics collection
- Added `/metrics` endpoint for Prometheus scraping
- Implemented comprehensive monitoring of:
  - Request rates and latencies by route type
  - Tool call success/failure rates
  - Cache hit/miss ratios
  - Fact checking results
  - RAG quality scores (faithfulness, relevancy, precision)
- Created Grafana dashboards for visualization
- Integrated RAGAS evaluation for offline and online quality assessment

## Architecture

```
POST /chat
   |
   v
Orchestrator
   |
   |--- Router (determines data source)
   |       |
   |       |--- RAG only
   |       |--- Tool only  
   |       |--- Tool + RAG
   |
   |--- Tool Service (5 banking APIs)
   |
   |--- RAG Service (document retrieval)
   |
   |--- LLM Service (generates final responses)
   |
   |--- Monitoring & Observability
           |
           |--- Prometheus Metrics
           |--- Grafana Dashboards  
           |--- RAGAS Evaluation
```

## Current Project Structure

- **app/** - Main application directory with all components
  - `api/` - API routers and endpoints
  - `core/` - Core configuration and settings  
  - `models/` - Data models for the application
  - `services/` - Business logic services
  - `tools/` - Banking tool implementations (to be implemented)
  - `rag/` - RAG pipeline components (to be implemented)
  - `monitoring/` - Monitoring and observability components
  - `tests/` - Test files

- **data/** - Directory for CSV data files (already populated with dummy data)

- **requirements.txt** - Complete list of dependencies

- **run.py** - Script to start the application