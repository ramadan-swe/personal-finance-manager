# tests/integration/user_management/test_login_cli.py
import pytest
from click.testing import CliRunner
from src.cli.user import register, login
from src.models.user_account import UserAccountPersistence
from src.services.session_manager import SessionManager
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup_state():
    # Ensure a clean state for each test
    if os.path.exists("user_accounts.json"):
        os.remove("user_accounts.json")
    SessionManager.logout_user()
    yield
    if os.path.exists("user_accounts.json"):
        os.remove("user_accounts.json")
    SessionManager.logout_user()

def test_login_success(runner):
    # First, register a user
    runner.invoke(register, ['--username', 'testuser', '--pin', '1234', '--pin', '1234'])
    
    result = runner.invoke(login, ['--username', 'testuser', '--pin', '1234'])
    assert "User 'testuser' logged in successfully." in result.output
    assert result.exit_code == 0
    assert SessionManager.is_logged_in() is True
    assert SessionManager.get_current_user().username == 'testuser'

def test_login_invalid_pin(runner):
    # First, register a user
    runner.invoke(register, ['--username', 'testuser', '--pin', '1234', '--pin', '1234'])

    result = runner.invoke(login, ['--username', 'testuser', '--pin', 'wrongpin'])
    assert "Error: Invalid username or PIN." in result.output
    assert result.exit_code == 0
    assert SessionManager.is_logged_in() is False

def test_login_non_existent_user(runner):
    result = runner.invoke(login, ['--username', 'nonexistent', '--pin', '1234'])
    assert "Error: Invalid username or PIN." in result.output
    assert result.exit_code == 0
    assert SessionManager.is_logged_in() is False
