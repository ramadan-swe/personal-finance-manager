# tests/integration/transaction_manager/test_delete_cli.py
import pytest
from click.testing import CliRunner
from src.cli.transaction import add, delete
from src.models.transaction import TransactionPersistence
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup_transactions():
    # Ensure a clean state for each test
    if os.path.exists("transactions.json"):
        os.remove("transactions.json")
    yield
    if os.path.exists("transactions.json"):
        os.remove("transactions.json")

def setup_transaction(runner):
    # Helper to add a transaction and return its ID
    runner.invoke(add, ['--amount', '100.00', '--date', '2025-10-24', '--type', 'income', '--description', 'Initial Salary', '--category', 'Salary'])
    persistence = TransactionPersistence()
    return persistence.get_all_transactions()[0].id

def test_delete_transaction_success(runner):
    transaction_id = setup_transaction(runner)
    result = runner.invoke(delete, ['--id', transaction_id], input='y\n') # Confirm deletion
    assert f"Transaction '{transaction_id}' deleted successfully." in result.output
    assert result.exit_code == 0
    persistence = TransactionPersistence()
    assert persistence.get_transaction(transaction_id) is None

def test_delete_transaction_cancel(runner):
    transaction_id = setup_transaction(runner)
    result = runner.invoke(delete, ['--id', transaction_id], input='n\n') # Cancel deletion
    assert "Deletion cancelled." in result.output
    assert result.exit_code == 0
    persistence = TransactionPersistence()
    assert persistence.get_transaction(transaction_id) is not None

def test_delete_transaction_not_found(runner):
    result = runner.invoke(delete, ['--id', 'non-existent'], input='y\n') # Confirm deletion
    assert "Error: Transaction 'non-existent' not found or failed to delete." in result.output
    assert result.exit_code == 0
