# tests/unit/user_management/test_authentication.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.user_management import UserManagementService
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

def test_authenticate_user_success(mock_persistence, user_service):
    username = "testuser"
    pin = "1234"
    salt = generate_salt()
    hashed_pin = hash_pin(pin, salt)
    mock_user_account = UserAccount(username, hashed_pin, salt)

    mock_persistence.get_account.return_value = mock_user_account

    authenticated_user = user_service.authenticate_user(username, pin)
    assert authenticated_user == mock_user_account
    mock_persistence.get_account.assert_called_once_with(username)

def test_authenticate_user_invalid_pin(mock_persistence, user_service):
    username = "testuser"
    correct_pin = "1234"
    wrong_pin = "4321"
    salt = generate_salt()
    hashed_pin = hash_pin(correct_pin, salt)
    mock_user_account = UserAccount(username, hashed_pin, salt)

    mock_persistence.get_account.return_value = mock_user_account

    authenticated_user = user_service.authenticate_user(username, wrong_pin)
    assert authenticated_user is None
    mock_persistence.get_account.assert_called_once_with(username)

def test_authenticate_user_non_existent_user(mock_persistence, user_service):
    username = "nonexistent"
    pin = "1234"

    mock_persistence.get_account.return_value = None

    authenticated_user = user_service.authenticate_user(username, pin)
    assert authenticated_user is None
    mock_persistence.get_account.assert_called_once_with(username)
