# tests/unit/transaction_manager/test_delete_transaction.py
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

def test_delete_transaction_success(mock_persistence, transaction_manager):
    transaction_id = "test-id-123"
    mock_persistence.delete_transaction.return_value = True

    result = transaction_manager.delete_transaction(transaction_id)
    assert result is True
    mock_persistence.delete_transaction.assert_called_once_with(transaction_id)

def test_delete_transaction_not_found(mock_persistence, transaction_manager):
    transaction_id = "non-existent-id"
    mock_persistence.delete_transaction.return_value = False

    result = transaction_manager.delete_transaction(transaction_id)
    assert result is False
    mock_persistence.delete_transaction.assert_called_once_with(transaction_id)
