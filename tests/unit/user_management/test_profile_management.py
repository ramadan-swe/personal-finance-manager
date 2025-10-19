# tests/unit/user_management/test_profile_management.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
from src.models.user_account import UserAccount
from src.utils.security import generate_salt, hash_pin

@pytest.fixture
def mock_persistence():
    with patch('src.services.user_management.UserAccountPersistence') as MockPersistence:
        persistence_instance = MockPersistence.return_value
        yield persistence_instance

@pytest.fixture
def user_service(mock_persistence):
    return UserManagementService()

@pytest.fixture(autouse=True)
def cleanup_session():
    SessionManager.logout_user()
    yield
    SessionManager.logout_user()

def test_update_profile_success(mock_persistence, user_service):
    username = "testuser"
    pin = "1234"
    salt = generate_salt()
    hashed_pin = hash_pin(pin, salt)
    user_account = UserAccount(username, hashed_pin, salt, {"name": "Old Name"})
    
    mock_persistence.update_account.return_value = True
    
    # Simulate user logged in
    SessionManager.login_user(user_account)
    
    user_account.profile_info['name'] = "New Name"
    assert user_service.update_profile(user_account) is True
    mock_persistence.update_account.assert_called_once_with(user_account)

def test_switch_user_success(mock_persistence, user_service):
    username1 = "user1"
    pin1 = "1111"
    salt1 = generate_salt()
    hashed_pin1 = hash_pin(pin1, salt1)
    user_account1 = UserAccount(username1, hashed_pin1, salt1)

    username2 = "user2"
    pin2 = "2222"
    salt2 = generate_salt()
    hashed_pin2 = hash_pin(pin2, salt2)
    user_account2 = UserAccount(username2, hashed_pin2, salt2)

    mock_persistence.get_account.side_effect = lambda u: {
        username1: user_account1,
        username2: user_account2
    }.get(u)

    # Login user1 first
    SessionManager.login_user(user_account1)
    assert SessionManager.get_current_user().username == username1

    # Simulate switching to user2 (authenticate_user is called internally by CLI command)
    authenticated_user2 = user_service.authenticate_user(username2, pin2)
    SessionManager.login_user(authenticated_user2) # This is what the CLI command would do

    assert SessionManager.get_current_user().username == username2

def test_logout_user(user_service):
    username = "testuser"
    pin = "1234"
    salt = generate_salt()
    hashed_pin = hash_pin(pin, salt)
    user_account = UserAccount(username, hashed_pin, salt)

    SessionManager.login_user(user_account)
    assert SessionManager.is_logged_in() is True

    SessionManager.logout_user()
    assert SessionManager.is_logged_in() is False
    assert SessionManager.get_current_user() is None
