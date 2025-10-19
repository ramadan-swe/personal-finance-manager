# tests/integration/user_management/test_register_cli.py
import pytest
from click.testing import CliRunner
from src.cli.user import register
from src.models.user_account import UserAccountPersistence
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup_user_accounts():
    # Ensure a clean state for each test
    if os.path.exists("user_accounts.json"):
        os.remove("user_accounts.json")
    yield
    if os.path.exists("user_accounts.json"):
        os.remove("user_accounts.json")

def test_register_success(runner):
    result = runner.invoke(register, ['--username', 'testuser', '--pin', '1234', '--pin', '1234'])
    assert "User 'testuser' registered successfully." in result.output
    assert result.exit_code == 0
    # Verify account exists in persistence
    persistence = UserAccountPersistence()
    assert persistence.get_account('testuser') is not None

def test_register_duplicate_username(runner):
    # Register first user
    runner.invoke(register, ['--username', 'testuser', '--pin', '1234', '--pin', '1234'])
    # Try to register again with same username
    result = runner.invoke(register, ['--username', 'testuser', '--pin', '5678', '--pin', '5678'])
    assert "Error: User 'testuser' already exists or registration failed." in result.output
    assert result.exit_code == 0
