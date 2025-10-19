# tests/unit/menu_manager/test_help_validation.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.menu_manager import MenuManager
from src.models.menu_item import MenuItem
from src.utils.input_validator import validate_integer, validate_currency, validate_iso_date, validate_pin, validate_yes_no, validate_category_name, validate_free_text

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

def test_get_contextual_help_for_item(menu_manager, mock_menu_item_persistence):
    item_id = "view_transactions"
    mock_menu_item_persistence.get_menu_item.return_value = MenuItem(item_id, "View Transactions", "command:view_transactions", "View all recorded transactions")
    
    help_text = menu_manager.get_contextual_help(menu_id="main", item_id=item_id)
    assert help_text == "View all recorded transactions"
    mock_menu_item_persistence.get_menu_item.assert_called_once_with(item_id)

def test_get_contextual_help_for_menu(menu_manager, mock_menu_item_persistence):
    menu_id = "main"
    mock_menu_item_persistence.get_all_menu_items.return_value = [
        MenuItem("view_transactions", "View Transactions", "command:view_transactions", "View all recorded transactions", parent_id="main"),
        MenuItem("add_transaction", "Add Transaction", "command:add_transaction", "Add a new financial transaction", parent_id="main"),
    ]
    
    help_text = menu_manager.get_contextual_help(menu_id=menu_id)
    assert "--- Help for Main Menu ---" in help_text
    assert "- View Transactions: View all recorded transactions" in help_text
    assert "- Add Transaction: Add a new financial transaction" in help_text
    assert "Q: Exit, B: Back, H: Help" in help_text

# --- Input Validator Tests ---

def test_validate_integer():
    assert validate_integer("123") == (True, 123)
    assert validate_integer("abc")[0] is False
    assert validate_integer("5", min_val=1, max_val=10) == (True, 5)
    assert validate_integer("0", min_val=1)[0] is False
    assert validate_integer("11", max_val=10)[0] is False

def test_validate_currency():
    assert validate_currency("$12.34") == (True, 12.34)
    assert validate_currency("12.34") == (True, 12.34)
    assert validate_currency("12")[0] is True
    assert validate_currency("$12")[0] is True
    assert validate_currency("12.345")[0] is False
    assert validate_currency("abc")[0] is False

def test_validate_iso_date():
    assert validate_iso_date("2025-10-24")[0] is True
    assert validate_iso_date("24-10-2025")[0] is False
    assert validate_iso_date("2025/10/24")[0] is False

def test_validate_pin():
    assert validate_pin("1234") == (True, "1234")
    assert validate_pin("123456") == (True, "123456")
    assert validate_pin("123")[0] is False # Too short
    assert validate_pin("1234567")[0] is False # Too long
    assert validate_pin("abcd")[0] is False # Non-digits

def test_validate_yes_no():
    assert validate_yes_no("y") == (True, True)
    assert validate_yes_no("yes") == (True, True)
    assert validate_yes_no("n") == (True, False)
    assert validate_yes_no("no") == (True, False)
    assert validate_yes_no("maybe")[0] is False

def test_validate_category_name():
    assert validate_category_name("Food")[0] is True
    assert validate_category_name("Food & Drink")[0] is False # Invalid char
    assert validate_category_name("Food-Drink")[0] is True
    assert validate_category_name("A"*65)[0] is False # Too long

def test_validate_free_text():
    assert validate_free_text("Some text")[0] is True
    assert validate_free_text("A"*1025)[0] is False # Too long
    assert validate_free_text(" ")[0] is False # Empty after strip
