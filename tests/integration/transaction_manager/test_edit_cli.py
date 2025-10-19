# tests/integration/transaction_manager/test_edit_cli.py
import pytest
from click.testing import CliRunner
from src.cli.transaction import add, edit
from src.models.transaction import TransactionPersistence, Transaction
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

def test_edit_transaction_success(runner):
    transaction_id = setup_transaction(runner)
    
    result = runner.invoke(edit, ['--id', transaction_id, '--amount', '120.00', '--description', 'Updated Salary'])
    assert f"Transaction '{transaction_id}' updated successfully." in result.output
    assert result.exit_code == 0
    
    persistence = TransactionPersistence()
    updated_transaction = persistence.get_transaction(transaction_id)
    assert updated_transaction.amount == 120.00
    assert updated_transaction.description == "Updated Salary"
    assert updated_transaction.date == "2025-10-24"

def test_edit_transaction_not_found(runner):
    result = runner.invoke(edit, ['--id', 'non-existent', '--amount', '50.00'])
    assert "Error: Transaction with ID 'non-existent' not found." in result.output
    assert result.exit_code == 0

def test_edit_transaction_invalid_amount(runner):
    transaction_id = setup_transaction(runner)
    result = runner.invoke(edit, ['--id', transaction_id, '--amount', 'abc'])
    assert "Error: Amount must be a number." in result.output
    assert result.exit_code == 0
    # Verify transaction was not updated
    persistence = TransactionPersistence()
    original_transaction = persistence.get_transaction(transaction_id)
    assert original_transaction.amount == 100.00
