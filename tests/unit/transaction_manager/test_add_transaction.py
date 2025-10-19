# tests/unit/transaction_manager/test_add_transaction.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.transaction_manager import TransactionManager
from src.models.transaction import Transaction

@pytest.fixture
def mock_persistence():
    with patch('src.services.transaction_manager.TransactionPersistence') as MockPersistence:
        persistence_instance = MockPersistence.return_value
        yield persistence_instance

@pytest.fixture
def transaction_manager(mock_persistence):
    return TransactionManager()

def test_add_transaction_success(mock_persistence, transaction_manager):
    mock_persistence.create_transaction.return_value = True
    
    amount = 100.0
    date = "2025-10-24"
    type = "income"
    description = "Salary"
    category = "Salary"
    
    result = transaction_manager.add_transaction(amount, date, type, description, category)
    assert result is True
    mock_persistence.create_transaction.assert_called_once()
    args, kwargs = mock_persistence.create_transaction.call_args
    created_transaction = args[0]
    assert isinstance(created_transaction, Transaction)
    assert created_transaction.amount == amount
    assert created_transaction.date == date
    assert created_transaction.type == type
    assert created_transaction.description == description
    assert created_transaction.category == category

def test_add_transaction_persistence_failure(mock_persistence, transaction_manager):
    mock_persistence.create_transaction.return_value = False
    
    amount = 100.0
    date = "2025-10-24"
    type = "income"
    description = "Salary"
    category = "Salary"
    
    result = transaction_manager.add_transaction(amount, date, type, description, category)
    assert result is False
    mock_persistence.create_transaction.assert_called_once()
