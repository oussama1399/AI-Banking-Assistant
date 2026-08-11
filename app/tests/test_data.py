"""
Test to verify CSV data structure and functionality
"""

import pandas as pd
import os

def test_csv_files_exist():
    """Test that all required CSV files exist"""
    required_files = [
        'data/customers.csv',
        'data/accounts.csv',
        'data/cards.csv',
        'data/transactions.csv',
        'data/transfers.csv'
    ]

    for file in required_files:
        assert os.path.exists(file), f"File {file} does not exist"

def test_csv_structure():
    """Test that CSV files have correct structure"""
    # Test customers.csv
    customers = pd.read_csv('data/customers.csv')
    expected_columns = ['customer_id', 'name', 'account_status', 'risk_profile']
    assert list(customers.columns) == expected_columns

    # Test accounts.csv
    accounts = pd.read_csv('data/accounts.csv')
    expected_columns = ['customer_id', 'account_type', 'available_balance', 'currency', 'account_status']
    assert list(accounts.columns) == expected_columns

    # Test cards.csv
    cards = pd.read_csv('data/cards.csv')
    expected_columns = ['customer_id', 'card_type', 'status', 'expiration_date', 'payment_limit', 'used_amount']
    assert list(cards.columns) == expected_columns

    # Test transactions.csv
    transactions = pd.read_csv('data/transactions.csv')
    expected_columns = ['transaction_id', 'customer_id', 'date', 'label', 'amount', 'currency']
    assert list(transactions.columns) == expected_columns

    # Test transfers.csv
    transfers = pd.read_csv('data/transfers.csv')
    expected_columns = ['transfer_id', 'amount', 'beneficiary', 'date', 'status', 'reason', 'customer_id']
    assert list(transfers.columns) == expected_columns

if __name__ == "__main__":
    test_csv_files_exist()
    test_csv_structure()
    print("All tests passed!")