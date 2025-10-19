# tests/unit/menu_manager/test_submenus.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.menu_manager import MenuManager
from src.models.menu_item import MenuItem
from src.models.menu_state import MenuState

@pytest.fixture
def mock_menu_item_persistence():
    with patch('src.services.menu_manager.MenuItemPersistence') as MockPersistence:
        persistence_instance = MockPersistence.return_value
        yield persistence_instance

@pytest.fixture
def mock_menu_state_persistence():
    with patch('src.services.menu_manager.MenuStatePersistence') as MockPersistence:
        persistence_instance = MockPersistence.return_value
        yield persistence_instance

@pytest.fixture
def menu_manager(mock_menu_item_persistence, mock_menu_state_persistence):
    # Prevent _initialize_default_menu from running during tests unless explicitly called
    mock_menu_item_persistence.get_all_menu_items.return_value = []
    manager = MenuManager()
    manager._initialize_default_menu = MagicMock() # Mock out initialization
    return manager

def test_navigate_to_submenu_new_state(menu_manager, mock_menu_state_persistence):
    user_id = "test_user"
    current_menu_id = "main"
    target_menu_id = "reports_menu"
    
    mock_menu_state_persistence.get_menu_state.return_value = None
    mock_menu_state_persistence.create_menu_state.return_value = True

    result = menu_manager.navigate_to_submenu(current_menu_id, target_menu_id, user_id)
    assert result == target_menu_id
    mock_menu_state_persistence.get_menu_state.assert_called_once_with(user_id)
    mock_menu_state_persistence.create_menu_state.assert_called_once()
    args, kwargs = mock_menu_state_persistence.create_menu_state.call_args
    created_state = args[0]
    assert created_state.user_id == user_id
    assert created_state.navigation_stack == [current_menu_id]

def test_navigate_to_submenu_existing_state(menu_manager, mock_menu_state_persistence):
    user_id = "test_user"
    current_menu_id = "main"
    target_menu_id = "reports_menu"
    existing_state = MenuState(user_id=user_id, navigation_stack=["start_menu"])
    
    mock_menu_state_persistence.get_menu_state.return_value = existing_state
    mock_menu_state_persistence.update_menu_state.return_value = True

    result = menu_manager.navigate_to_submenu(current_menu_id, target_menu_id, user_id)
    assert result == target_menu_id
    mock_menu_state_persistence.get_menu_state.assert_called_once_with(user_id)
    mock_menu_state_persistence.update_menu_state.assert_called_once()
    assert existing_state.navigation_stack == ["start_menu", current_menu_id]

def test_return_to_parent_menu_success(menu_manager, mock_menu_state_persistence):
    user_id = "test_user"
    current_menu_id = "reports_menu"
    existing_state = MenuState(user_id=user_id, navigation_stack=["main", "settings_menu"])
    
    mock_menu_state_persistence.get_menu_state.return_value = existing_state
    mock_menu_state_persistence.update_menu_state.return_value = True

    result = menu_manager.return_to_parent_menu(current_menu_id, user_id)
    assert result == "settings_menu"
    mock_menu_state_persistence.get_menu_state.assert_called_once_with(user_id)
    mock_menu_state_persistence.update_menu_state.assert_called_once()
    assert existing_state.navigation_stack == ["main"]

def test_return_to_parent_menu_empty_stack(menu_manager, mock_menu_state_persistence):
    user_id = "test_user"
    current_menu_id = "main"
    existing_state = MenuState(user_id=user_id, navigation_stack=[])
    
    mock_menu_state_persistence.get_menu_state.return_value = existing_state

    result = menu_manager.return_to_parent_menu(current_menu_id, user_id)
    assert result == "main" # Fallback to main
    mock_menu_state_persistence.get_menu_state.assert_called_once_with(user_id)
    mock_menu_state_persistence.update_menu_state.assert_not_called()
