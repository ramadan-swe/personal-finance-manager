# tests/integration/transaction_manager/test_add_cli.py
import pytest
from click.testing import CliRunner
from src.cli.transaction import add
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

def test_add_transaction_success(runner):
    result = runner.invoke(add, ['--amount', '50.00', '--date', '2025-10-24', '--type', 'expense', '--description', 'Groceries', '--category', 'Food'])
    assert "Transaction added successfully." in result.output
    assert result.exit_code == 0
    
    persistence = TransactionPersistence()
    transactions = persistence.get_all_transactions()
    assert len(transactions) == 1
    assert transactions[0].amount == 50.00
    assert transactions[0].description == "Groceries"

def test_add_transaction_invalid_amount(runner):
    result = runner.invoke(add, ['--amount', 'abc', '--date', '2025-10-24', '--type', 'expense', '--description', 'Groceries', '--category', 'Food'])
    assert "Error: Amount must be a number." in result.output
    assert result.exit_code == 0
    persistence = TransactionPersistence()
    assert len(persistence.get_all_transactions()) == 0

def test_add_transaction_invalid_date(runner):
    result = runner.invoke(add, ['--amount', '50.00', '--date', '24-10-2025', '--type', 'expense', '--description', 'Groceries', '--category', 'Food'])
    assert "Error: Date must be in YYYY-MM-DD format." in result.output
    assert result.exit_code == 0
    persistence = TransactionPersistence()
    assert len(persistence.get_all_transactions()) == 0

def test_add_transaction_invalid_type(runner):
    result = runner.invoke(add, ['--amount', '50.00', '--date', '2025-10-24', '--type', 'invalid', '--description', 'Groceries', '--category', 'Food'])
    assert "Error: Invalid value for '--type': 'invalid' is not one of 'income', 'expense'." in result.output
    assert result.exit_code == 2 # click exits with 2 for invalid choices
    persistence = TransactionPersistence()
    assert len(persistence.get_all_transactions()) == 0

def test_add_transaction_invalid_category(runner):
    result = runner.invoke(add, ['--amount', '50.00', '--date', '2025-10-24', '--type', 'expense', '--description', 'Groceries', '--category', 'InvalidCategory'])
    assert "Error: Invalid category 'InvalidCategory'. Use 'finance category list' to see available categories." in result.output
    assert result.exit_code == 0
    persistence = TransactionPersistence()
    assert len(persistence.get_all_transactions()) == 0
