# tests/unit/menu_manager/test_primary_menu.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.menu_manager import MenuManager
from src.models.menu_item import MenuItem

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

def test_get_primary_menu(menu_manager, mock_menu_item_persistence):
    # Setup mock data for primary menu
    mock_menu_item_persistence.get_all_menu_items.return_value = [
        MenuItem("view_transactions", "View Transactions", "command:view_transactions", "", parent_id="main"),
        MenuItem("add_transaction", "Add Transaction", "command:add_transaction", "", parent_id="main"),
        MenuItem("reports_menu", "Reports", "menu:reports", "", parent_id="main"),
        MenuItem("some_submenu_item", "Submenu Item", "command:do_something", "", parent_id="reports_menu"),
    ]
    
    primary_menu = menu_manager.get_primary_menu()
    assert len(primary_menu) == 3
    assert all(item.parent_id == "main" for item in primary_menu)
    assert primary_menu[0].id == "view_transactions"

def test_display_menu(menu_manager, mock_menu_item_persistence):
    mock_stdscr = MagicMock() # Mock curses screen
    
    # Setup mock data for primary menu
    mock_menu_item_persistence.get_all_menu_items.return_value = [
        MenuItem("view_transactions", "View Transactions", "command:view_transactions", "", parent_id="main"),
        MenuItem("add_transaction", "Add Transaction", "command:add_transaction", "", parent_id="main"),
    ]
    
    menu_manager.display_menu(mock_stdscr, "main")
    
    # Verify display_message was called for each item and menu title/exit option
    mock_stdscr.clear.assert_called_once()
    assert mock_stdscr.addstr.call_count >= 5 # Title, 2 items, Exit, Prompt
    mock_stdscr.refresh.assert_called()
