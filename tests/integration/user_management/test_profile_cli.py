# tests/integration/user_management/test_profile_cli.py
import pytest
from click.testing import CliRunner
from src.cli.user import register, login, update_profile_command, switch, logout
from src.models.user_account import UserAccountPersistence
from src.services.session_manager import SessionManager
import os
import json

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

def register_and_login(runner, username, pin):
    runner.invoke(register, ['--username', username, '--pin', pin, '--pin', pin])
    runner.invoke(login, ['--username', username, '--pin', pin])

def test_update_profile_success(runner):
    register_and_login(runner, 'testuser', '1234')
    
    result = runner.invoke(update_profile_command, ['--name', 'New Name', '--preferences', '{"theme": "dark"}'])
    assert "Profile updated successfully." in result.output
    assert result.exit_code == 0
    
    current_user = SessionManager.get_current_user()
    assert current_user.profile_info.get('name') == 'New Name'
    assert current_user.profile_info.get('theme') == 'dark'

def test_update_profile_not_logged_in(runner):
    result = runner.invoke(update_profile_command, ['--name', 'New Name'])
    assert "Error: No user is currently logged in." in result.output
    assert result.exit_code == 0

def test_switch_user_success(runner):
    register_and_login(runner, 'user1', '1111')
    runner.invoke(register, ['--username', 'user2', '--pin', '2222', '--pin', '2222'])

    result = runner.invoke(switch, ['--username', 'user2', '--pin', '2222'])
    assert "Switched to user 'user2' successfully." in result.output
    assert result.exit_code == 0
    assert SessionManager.get_current_user().username == 'user2'

def test_switch_user_data_leakage_prevention(runner):
    # Register and login user1, set a profile preference
    register_and_login(runner, 'user1', '1111')
    runner.invoke(update_profile_command, ['--preferences', '{"secret_data": "user1_secret"}'])
    
    # Register and login user2
    runner.invoke(register, ['--username', 'user2', '--pin', '2222', '--pin', '2222'])
    runner.invoke(login, ['--username', 'user2', '--pin', '2222'])

    # Verify user2 does not have user1's secret data
    current_user2 = SessionManager.get_current_user()
    assert current_user2.username == 'user2'
    assert 'secret_data' not in current_user2.profile_info

    # Switch back to user1 and verify data is still there
    runner.invoke(switch, ['--username', 'user1', '--pin', '1111'])
    current_user1 = SessionManager.get_current_user()
    assert current_user1.username == 'user1'
    assert current_user1.profile_info.get('secret_data') == 'user1_secret'

def test_logout_success(runner):
    register_and_login(runner, 'testuser', '1234')
    result = runner.invoke(logout)
    assert "User 'testuser' logged out successfully." in result.output
    assert result.exit_code == 0
    assert SessionManager.is_logged_in() is False
