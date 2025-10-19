# tests/integration/menu_manager/test_submenu_cli.py
import pytest
from click.testing import CliRunner
from src.cli.menu import start
from src.models.menu_item import MenuItemPersistence, MenuItem
from src.models.menu_state import MenuStatePersistence
from unittest.mock import patch, MagicMock
import curses
import os

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def cleanup_state():
    # Ensure a clean state for each test
    if os.path.exists("menu_items.json"):
        os.remove("menu_items.json")
    if os.path.exists("menu_states.json"):
        os.remove("menu_states.json")
    yield
    if os.path.exists("menu_items.json"):
        os.remove("menu_items.json")
    if os.path.exists("menu_states.json"):
        os.remove("menu_states.json")

@pytest.fixture
def setup_full_menu():
    persistence = MenuItemPersistence()
    persistence.create_menu_item(MenuItem("main", "Main Menu", "", "Top level menu"))
    persistence.create_menu_item(MenuItem("view_transactions", "View Transactions", "command:view_transactions", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("reports_menu", "Reports", "menu:reports", "", parent_id="main"))
    persistence.create_menu_item(MenuItem("settings_menu", "Settings", "menu:settings", "", parent_id="main"))

    persistence.create_menu_item(MenuItem("reports", "Reports Menu", "", "Financial reports", parent_id="reports_menu"))
    persistence.create_menu_item(MenuItem("monthly_report", "Monthly Report", "command:monthly_report", "Generate monthly financial report", parent_id="reports_menu"))
    persistence.create_menu_item(MenuItem("category_breakdown", "Category Breakdown", "command:category_breakdown", "View spending by category", parent_id="reports_menu"))

    persistence.create_menu_item(MenuItem("settings", "Settings Menu", "", "Application settings", parent_id="settings_menu"))
    persistence.create_menu_item(MenuItem("change_pin", "Change PIN", "command:change_pin", "Change user PIN", parent_id="settings_menu"))

@patch('src.utils.curses_utils.init_curses')
@patch('src.utils.curses_utils.teardown_curses')
@patch('src.utils.curses_utils.display_message')
@patch('src.utils.curses_utils.get_user_input')
def test_drill_down_and_back_navigation(mock_get_user_input, mock_display_message, mock_teardown_curses, mock_init_curses, runner, setup_full_menu):
    mock_stdscr = MagicMock()
    mock_init_curses.return_value = mock_stdscr
    # Sequence: Go to Reports (3), then Back (B), then Exit (Q)
    mock_get_user_input.side_effect = ['3', 'B', 'Q']

    result = runner.invoke(start)
    assert result.exit_code == 0
    mock_init_curses.assert_called_once()
    mock_teardown_curses.assert_called_once_with(mock_stdscr)

    # Verify main menu displayed first
    mock_display_message.assert_any_call(mock_stdscr, "--- Main Menu ---", 0, 0)
    # Verify reports menu displayed after selecting 3
    mock_display_message.assert_any_call(mock_stdscr, "--- Reports Menu ---", 0, 0)
    # Verify main menu displayed again after selecting B
    mock_display_message.assert_any_call(mock_stdscr, "--- Main Menu ---", 0, 0)

@patch('src.utils.curses_utils.init_curses')
@patch('src.utils.curses_utils.teardown_curses')
@patch('src.utils.curses_utils.display_message')
@patch('src.utils.curses_utils.get_user_input')
def test_drill_down_multiple_levels(mock_get_user_input, mock_display_message, mock_teardown_curses, mock_init_curses, runner, setup_full_menu):
    mock_stdscr = MagicMock()
    mock_init_curses.return_value = mock_stdscr
    # Sequence: Go to Reports (3), then Monthly Report (1 - which is a command), then Back (B), then Exit (Q)
    mock_get_user_input.side_effect = ['3', '1', 'B', 'Q']

    result = runner.invoke(start)
    assert result.exit_code == 0

    # Verify Reports menu displayed
    mock_display_message.assert_any_call(mock_stdscr, "--- Reports Menu ---", 0, 0)
    # Verify command execution message for Monthly Report
    mock_display_message.assert_any_call(mock_stdscr, "Executing: command:monthly_report", 5, 0)
    # Verify Reports menu displayed again after command execution (and implicit back)
    mock_display_message.assert_any_call(mock_stdscr, "--- Reports Menu ---", 0, 0)
    # Verify main menu displayed after selecting B
    mock_display_message.assert_any_call(mock_stdscr, "--- Main Menu ---", 0, 0)
