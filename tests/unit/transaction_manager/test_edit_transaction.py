# tests/unit/transaction_manager/test_edit_transaction.py
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

def test_update_transaction_success(mock_persistence, transaction_manager):
    transaction_id = "test-id-123"
    original_transaction = Transaction(100.0, "2025-10-24", "income", "Salary", "Salary", id=transaction_id)
    mock_persistence.get_transaction.return_value = original_transaction
    mock_persistence.update_transaction.return_value = True

    updates = {"amount": 120.0, "description": "Monthly Salary"}
    result = transaction_manager.update_transaction(transaction_id, **updates)
    assert result is True
    mock_persistence.get_transaction.assert_called_once_with(transaction_id)
    mock_persistence.update_transaction.assert_called_once()
    
    updated_transaction = mock_persistence.update_transaction.call_args[0][0]
    assert updated_transaction.amount == 120.0
    assert updated_transaction.description == "Monthly Salary"
    assert updated_transaction.date == "2025-10-24" # Unchanged

def test_update_transaction_not_found(mock_persistence, transaction_manager):
    transaction_id = "non-existent-id"
    mock_persistence.get_transaction.return_value = None

    updates = {"amount": 120.0}
    result = transaction_manager.update_transaction(transaction_id, **updates)
    assert result is False
    mock_persistence.get_transaction.assert_called_once_with(transaction_id)
    mock_persistence.update_transaction.assert_not_called()

def test_update_transaction_persistence_failure(mock_persistence, transaction_manager):
    transaction_id = "test-id-123"
    original_transaction = Transaction(100.0, "2025-10-24", "income", "Salary", "Salary", id=transaction_id)
    mock_persistence.get_transaction.return_value = original_transaction
    mock_persistence.update_transaction.return_value = False

    updates = {"amount": 120.0}
    result = transaction_manager.update_transaction(transaction_id, **updates)
    assert result is False
    mock_persistence.get_transaction.assert_called_once_with(transaction_id)
    mock_persistence.update_transaction.assert_called_once()
