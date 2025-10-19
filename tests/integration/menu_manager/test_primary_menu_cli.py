# tests/integration/menu_manager/test_primary_menu_cli.py
import pytest
from click.testing import CliRunner
from src.cli.menu import start
from src.models.menu_item import MenuItemPersistence, MenuItem
from unittest.mock import patch, MagicMock
import curses
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup_menu_items():
    # Ensure a clean state for each test
    if os.path.exists("menu_items.json"):
        os.remove("menu_items.json")
    yield
    if os.path.exists("menu_items.json"):
        os.remove("menu_items.json")

@pytest.fixture
def setup_default_menu():
    persistence = MenuItemPersistence()
    persistence.create_menu_item(MenuItem("main", "Main Menu", "", "Top level menu"))
    persistence.create_menu_item(MenuItem("view_transactions", "View Transactions", "command:view_transactions", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("add_transaction", "Add Transaction", "command:add_transaction", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("reports_menu", "Reports", "menu:reports", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("settings_menu", "Settings", "menu:settings", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("reports", "Reports Menu", "", "", parent_id="reports_menu"))
    persistence.create_menu_item(MenuItem("monthly_report", "Monthly Report", "command:monthly_report", "", parent_id="reports_menu"))
    persistence.create_menu_item(MenuItem("settings", "Settings Menu", "", "", parent_id="settings_menu"))
    persistence.create_menu_item(MenuItem("change_pin", "Change PIN", "command:change_pin", "", parent_id="settings_menu"))

@patch('src.utils.curses_utils.init_curses')
@patch('src.utils.curses_utils.teardown_curses')
@patch('src.utils.curses_utils.display_message')
@patch('src.utils.curses_utils.get_user_input')
def test_start_menu_exit(mock_get_user_input, mock_display_message, mock_teardown_curses, mock_init_curses, runner, setup_default_menu):
    mock_stdscr = MagicMock()
    mock_init_curses.return_value = mock_stdscr
    mock_get_user_input.side_effect = ['Q'] # User exits immediately

    result = runner.invoke(start)
    assert result.exit_code == 0
    mock_init_curses.assert_called_once()
    mock_teardown_curses.assert_called_once_with(mock_stdscr)
    mock_display_message.assert_any_call(mock_stdscr, "--- Main Menu ---", 0, 0)
    mock_display_message.assert_any_call(mock_stdscr, "1. View Transactions", 1, 0)
    mock_display_message.assert_any_call(mock_stdscr, "Q. Exit", 5, 0)

@patch('src.utils.curses_utils.init_curses')
@patch('src.utils.curses_utils.teardown_curses')
@patch('src.utils.curses_utils.display_message')
@patch('src.utils.curses_utils.get_user_input')
def test_start_menu_invalid_choice(mock_get_user_input, mock_display_message, mock_teardown_curses, mock_init_curses, runner, setup_default_menu):
    mock_stdscr = MagicMock()
    mock_init_curses.return_value = mock_stdscr
    mock_get_user_input.side_effect = ['99', 'Q'] # Invalid choice then exit

    result = runner.invoke(start)
    assert result.exit_code == 0
    mock_display_message.assert_any_call(mock_stdscr, "Invalid choice.", 6, 0)
    mock_display_message.assert_any_call(mock_stdscr, "Enter your choice: ", 6, 0) # Re-prompt

@patch('src.utils.curses_utils.init_curses')
@patch('src.utils.curses_utils.teardown_curses')
@patch('src.utils.curses_utils.display_message')
@patch('src.utils.curses_utils.get_user_input')
def test_start_menu_navigate_to_submenu_and_exit(mock_get_user_input, mock_display_message, mock_teardown_curses, mock_init_curses, runner, setup_default_menu):
    mock_stdscr = MagicMock()
    mock_init_curses.return_value = mock_stdscr
    mock_get_user_input.side_effect = ['3', 'Q'] # Choose Reports (3), then Exit

    result = runner.invoke(start)
    assert result.exit_code == 0
    # Verify Reports menu was displayed
    mock_display_message.assert_any_call(mock_stdscr, "--- Reports Menu ---", 0, 0)
    mock_display_message.assert_any_call(mock_stdscr, "1. Monthly Report", 1, 0)
    mock_display_message.assert_any_call(mock_stdscr, "Q. Exit", 3, 0)
    mock_display_message.assert_any_call(mock_stdscr, "B. Back", 4, 0)
