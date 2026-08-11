"""
Mock banking tools for AI Banking Assistant
"""

import pandas as pd
import os
from typing import Dict, Any, Optional
from pathlib import Path

def get_account_balance(customer_id: str) -> Dict[str, Any]:
    """
    Get account balance for a customer

    Args:
        customer_id (str): Unique identifier for the customer

    Returns:
        Dict containing account information

    Raises:
        Exception: If customer is not found
    """
    try:
        # Define the path to the accounts CSV file
        data_path = Path("data/accounts.csv")

        # Check if file exists
        if not data_path.exists():
            raise FileNotFoundError(f"Accounts data file not found at {data_path}")

        # Read the CSV file
        accounts_df = pd.read_csv(data_path)

        # Find the customer's account
        customer_account = accounts_df[accounts_df['customer_id'] == customer_id]

        # Check if account exists
        if customer_account.empty:
            raise Exception("customer_not_found")

        # Get the first (and should be only) matching account
        account_data = customer_account.iloc[0]

        # Return structured response
        return {
            "customer_id": customer_id,
            "available_balance": float(account_data['available_balance']),
            "currency": account_data['currency'],
            "account_type": account_data['account_type']
        }

    except Exception as e:
        # Re-raise with more specific error handling if needed
        raise Exception(f"Error retrieving account balance for {customer_id}: {str(e)}")

def get_transactions(customer_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list:
    """
    Get transaction history for a customer

    Args:
        customer_id (str): Unique identifier for the customer
        start_date (str, optional): Start date filter
        end_date (str, optional): End date filter

    Returns:
        List of transaction dictionaries
    """
    try:
        data_path = Path("data/transactions.csv")

        if not data_path.exists():
            raise FileNotFoundError(f"Transactions data file not found at {data_path}")

        transactions_df = pd.read_csv(data_path)
        customer_transactions = transactions_df[transactions_df['customer_id'] == customer_id]

        if customer_transactions.empty:
            return []

        # Convert to list of dictionaries
        transactions_list = []
        for _, row in customer_transactions.iterrows():
            transactions_list.append({
                "transaction_id": row['transaction_id'],
                "date": row['date'],
                "label": row['label'],
                "amount": float(row['amount']),
                "currency": row['currency']
            })

        return transactions_list

    except Exception as e:
        raise Exception(f"Error retrieving transactions for {customer_id}: {str(e)}")

def get_card_info(customer_id: str) -> Dict[str, Any]:
    """
    Get card information for a customer

    Args:
        customer_id (str): Unique identifier for the customer

    Returns:
        Dict containing card information

    Raises:
        Exception: If customer is not found
    """
    try:
        data_path = Path("data/cards.csv")

        if not data_path.exists():
            raise FileNotFoundError(f"Cards data file not found at {data_path}")

        cards_df = pd.read_csv(data_path)
        customer_card = cards_df[cards_df['customer_id'] == customer_id]

        if customer_card.empty:
            raise Exception("customer_not_found")

        card_data = customer_card.iloc[0]

        return {
            "customer_id": customer_id,
            "card_type": card_data['card_type'],
            "status": card_data['status'],
            "expiration_date": card_data['expiration_date'],
            "payment_limit": float(card_data['payment_limit']),
            "used_amount": float(card_data['used_amount'])
        }

    except Exception as e:
        raise Exception(f"Error retrieving card info for {customer_id}: {str(e)}")

def get_transfer_status(transfer_id: str) -> Dict[str, Any]:
    """
    Get status of a transfer

    Args:
        transfer_id (str): Unique identifier for the transfer

    Returns:
        Dict containing transfer information

    Raises:
        Exception: If transfer is not found
    """
    try:
        data_path = Path("data/transfers.csv")

        if not data_path.exists():
            raise FileNotFoundError(f"Transfers data file not found at {data_path}")

        transfers_df = pd.read_csv(data_path)
        transfer = transfers_df[transfers_df['transfer_id'] == transfer_id]

        if transfer.empty:
            raise Exception("transfer_not_found")

        transfer_data = transfer.iloc[0]

        return {
            "transfer_id": transfer_id,
            "amount": float(transfer_data['amount']),
            "beneficiary": transfer_data['beneficiary'],
            "date": transfer_data['date'],
            "status": transfer_data['status'],
            "reason": transfer_data['reason'] if not pd.isna(transfer_data['reason']) else None
        }

    except Exception as e:
        raise Exception(f"Error retrieving transfer status for {transfer_id}: {str(e)}")

def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """
    Get customer information

    Args:
        customer_id (str): Unique identifier for the customer

    Returns:
        Dict containing customer information

    Raises:
        Exception: If customer is not found
    """
    try:
        data_path = Path("data/customers.csv")

        if not data_path.exists():
            raise FileNotFoundError(f"Customers data file not found at {data_path}")

        customers_df = pd.read_csv(data_path)
        customer = customers_df[customers_df['customer_id'] == customer_id]

        if customer.empty:
            raise Exception("customer_not_found")

        customer_data = customer.iloc[0]

        return {
            "customer_id": customer_id,
            "name": customer_data['name'],
            "account_status": customer_data['account_status'],
            "risk_profile": customer_data['risk_profile']
        }

    except Exception as e:
        raise Exception(f"Error retrieving customer info for {customer_id}: {str(e)}")

# Test function to verify the tools work correctly
def test_all_tools():
    """Test that all tools can be imported and work correctly"""
    print("Testing banking tools...")

    # Test account balance
    try:
        result = get_account_balance("C1024")
        print(f"✓ Account balance for C1024: {result}")
    except Exception as e:
        print(f"✗ Error with account balance: {e}")

    # Test customer info
    try:
        result = get_customer_info("C1024")
        print(f"✓ Customer info for C1024: {result}")
    except Exception as e:
        print(f"✗ Error with customer info: {e}")

    # Test card info
    try:
        result = get_card_info("C1024")
        print(f"✓ Card info for C1024: {result}")
    except Exception as e:
        print(f"✗ Error with card info: {e}")

    # Test transfer status
    try:
        result = get_transfer_status("TR4587")
        print(f"✓ Transfer status for TR4587: {result}")
    except Exception as e:
        print(f"✗ Error with transfer status: {e}")

if __name__ == "__main__":
    test_all_tools()