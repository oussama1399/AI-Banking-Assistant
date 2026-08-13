# AI Banking Assistant

## Description

AI Banking Assistant is an intelligent chatbot system that provides banking information to customers. It can answer questions about account balances, transactions, card status, transfer status, and general banking procedures by intelligently routing queries between tools and a knowledge base.

## Architecture

```
POST /api/v1/chat
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
```

## Project Structure

```
app/
├── api/                 # API endpoints and routers
│   └── chat.py          # Main chat endpoint implementation
├── core/                # Core configuration and settings
│   └── config.py        # Application configuration
├── models/              # Data models for the application
│   └── chat.py          # Chat request/response models
├── services/            # Business logic services
│   ├── orchestrator.py  # Coordination of components
│   ├── router.py        # Intelligent routing system
│   ├── tool_service.py  # Banking tool service implementation
│   ├── rag_service.py   # RAG knowledge base service
│   ├── llm_service.py   # LLM response generation
│   └── prompts.py       # Prompt templates for LLM
├── tools/               # Mock banking tools
│   └── banking_tools.py # Implementation of 5 banking tools
├── rag/                 # RAG pipeline components
│   └── rag_pipeline.py  # RAG document processing and retrieval
├── monitoring/          # Monitoring and observability
│   ├── __init__.py      # Monitoring package
│   └── metrics.py       # Prometheus metrics collection
└── tests/               # Test files
    ├── test_api.py      # API endpoint tests
    ├── test_router.py   # Router tests
    ├── test_tools.py    # Tool service tests
    └── test_metrics.py  # Metrics tests

data/                    # CSV data files for mock data
├── customers.csv        # Customer information
├── accounts.csv         # Account details  
├── cards.csv            # Card information
├── transactions.csv     # Transaction history
└── knowledge_base/      # RAG documents (Markdown files)
    ├── account_policies.md
    ├── card_policies.md
    ├── fraud_policy.md
    ├── international_transfers.md
    ├── loans.md
    ├── lost_card_procedure.md
    └── transfer_policies.md

run.py                   # Main application entry point
requirements.txt         # Dependencies
README.md                # This documentation file
```

## Data Structure

The system uses the following CSV files for mock data:

### customers.csv
- customer_id: Unique identifier for the customer
- name: Customer's full name
- account_status: Status of the customer's account (active/inactive)
- risk_profile: Risk profile level (low/medium/high/standard)

### accounts.csv
- customer_id: Reference to the customer
- account_type: Type of account (current/savings/checking)
- available_balance: Current available balance
- currency: Currency of the account
- account_status: Status of the account

### cards.csv
- customer_id: Reference to the customer
- card_type: Type of card (Standard/Gold/Platinum)
- status: Status of the card (active/inactive)
- expiration_date: Expiration date of the card
- payment_limit: Maximum spending limit
- used_amount: Amount already spent

### transactions.csv
- transaction_id: Unique identifier for the transaction
- customer_id: Reference to the customer
- date: Date of the transaction
- label: Description of the transaction
- amount: Transaction amount (negative for expenses)
- currency: Currency of the transaction

### transfers.csv
- transfer_id: Unique identifier for the transfer
- amount: Transfer amount
- beneficiary: Name of the beneficiary
- date: Date of the transfer
- status: Status of the transfer (pending/completed/rejected)
- reason: Reason for rejection (if applicable)
- customer_id: Reference to the customer

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

The application will start on port 8090 by default.

The application will start on port 8081 by default.

## API Endpoints

### POST /api/v1/chat
Main chat endpoint for banking assistant.

**Request Body:**
```json
{
  "customer_id": "C1024",
  "message": "Quel est le statut de mon virement TR4587 ?"
}
```

**Response Format:**
```json
{
  "answer": "Response text in French",
  "source": "get_account_balance|get_transfer_status|RAG|get_card_info|get_transactions|get_customer_info|tool+RAG",
  "documents": ["document1.md", "document2.md"]  // Only for RAG responses
}
```

### GET /health
Health check endpoint.

### GET /metrics
Prometheus metrics endpoint.

## Usage Examples

### Tool-only query:
```json
{
  "customer_id": "C1024",
  "message": "Quel est mon solde ?"
}
```
Response:
```json
{
  "answer": "Votre solde disponible est de 2450.75 EUR.",
  "source": "get_account_balance"
}
```

### RAG-only query:
```json
{
  "customer_id": "C1024",
  "message": "Quels sont les frais pour un virement international ?"
}
```
Response:
```json
{
  "answer": "Les virements internationaux peuvent inclure des frais d'émission, des frais de banque intermédiaire et des frais de conversion.",
  "source": "RAG"
}
```

### Tool + RAG query:
```json
{
  "customer_id": "C1024",
  "message": "Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ?"
}
```
Response:
```json
{
  "answer": "Votre virement TR4587 a été refusé pour solde insuffisant. Veuillez vérifier votre solde ou réduire le montant du virement.",
  "source": "get_transfer_status+RAG"
}
```

## Streamlit Frontend

The Streamlit application is configured to connect to the backend on port 8090 by default. When running the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The frontend will automatically connect to `http://localhost:8090/api/v1/chat`

## Implementation Approach

Follows the roadmap with:
1. Setup and mock tools creation
2. RAG pipeline implementation
3. Router development
4. FastAPI endpoint integration
5. Error handling and testing

## Monitoring & Metrics

The application exposes Prometheus-compatible metrics at `/metrics` endpoint. The monitoring includes:

- Chat requests by route type (tool, rag, tool+rag, clarification)
- Request latency distribution
- Tool call success/failure rates
- RAG query performance
- Error tracking by error type

You can view these metrics using:
- Direct access to `/metrics` endpoint
- Prometheus scraping
- Grafana dashboards (if configured)

The application runs on port 8090, which is configured in the monitoring system.


## Features

### Intelligent Routing
The system intelligently routes questions based on keywords and context:
- **RAG-only**: General questions about banking procedures
- **Tool-only**: Personal account inquiries (balance, transactions, etc.)
- **Tool + RAG**: Complex questions requiring both personal data and general knowledge
- **Clarification**: Requests for missing parameters

### Banking Tools (5 Services)
1. `get_account_balance(customer_id)` - Get account balance
2. `get_transactions(customer_id, start_date=None, end_date=None)` - Get transaction history  
3. `get_card_info(customer_id)` - Get card information
4. `get_transfer_status(transfer_id)` - Get transfer status
5. `get_customer_info(customer_id)` - Get customer profile

### RAG Knowledge Base
- Documents covering various banking topics in Markdown format
- Retrieval-Augmented Generation pipeline with ChromaDB storage
- Sentence transformers for semantic search

### Error Handling
- Comprehensive error handling with user-friendly messages
- Detailed logging for debugging
- Graceful degradation when services are unavailable

## Dependencies

The application requires the following dependencies (from requirements.txt):
- FastAPI and Uvicorn for web server
- Pydantic for data validation
- Pandas for data processing
- ChromaDB and Sentence Transformers for RAG
- LangChain for LLM integration
- Prometheus client for metrics
- pytest for testing

## Security Considerations

- Input validation using Pydantic models
- CORS middleware configuration
- Secure handling of customer identifiers
- No sensitive data storage or transmission

## Performance Characteristics

- Asynchronous API endpoints
- Lazy initialization of heavy components
- Caching capabilities
- Prometheus-based performance monitoring

## Port Configuration

The application is configured to run on port 8090 by default, which resolves conflicts with previous ports (8080 and 8081). This ensures consistent startup behavior across different environments.

To change the port:
1. Update `run.py` file to modify the port parameter
2. Update `streamlit_app.py` to change the API URL 
3. Update `prometheus.yml` to scrape from the new port