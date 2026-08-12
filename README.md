# AI Banking Assistant

## Description
AI Banking Assistant is an intelligent chatbot system that provides banking information to customers. It can answer questions about account balances, transactions, card status, transfer status, and general banking procedures by intelligently routing queries between tools and a knowledge base.

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
1. Create a virtual environment
2. Install dependencies: `pip install -r requirements.txt`

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

## Implementation Approach
Follows the roadmap in roadmap.md with:
1. Setup and mock tools creation
2. RAG pipeline implementation
3. Router development
4. FastAPI endpoint integration
5. Error handling and testing

## Metrics & Monitoring
The application exposes Prometheus-compatible metrics at `/metrics`. 
You can view these metrics using:
- `python simple_metrics.py` for console output
- `streamlit run metrics_dashboard.py` for web interface

This provides visibility into chat requests, response times, and system performance.