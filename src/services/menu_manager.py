from datetime import date
from src.utils.prompt_toolkit_utils import display_menu, get_user_input, add_message, print_formatted_text
from src.utils.input_validator import validate_number, validate_iso_date, validate_type, validate_description, validate_category, validate_pin
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import get_categories, is_valid_category
from src.services.session_manager import SessionManager
from src.services.user_management import UserManagementService
from src.services.data_persistence import DataPersistenceService
from src.cli.user import update_profile_command, switch, logout
from src.cli.transaction import add_transaction_command, edit_transaction_command, delete_transaction_command

# Global variables for menu management
_navigation_stack = []

# Hardcoded menu structure
_ALL_MENUS = {
    "main": {
        "label": "Main Menu",
        "items": [
            {"id": "view_transactions", "label": "View Transactions", "action": "command:view_transactions", "help_text": "View all recorded transactions"},
            {"id": "add_transaction", "label": "Add Transaction", "action": "command:add_transaction", "help_text": "Add a new financial transaction"},
            {"id": "reports_menu", "label": "Reports", "action": "menu:reports", "help_text": "Access financial reports"},
            {"id": "settings_menu", "label": "Settings", "action": "menu:settings", "help_text": "Configure application settings"},
        ]
    },
    "reports": {
        "label": "Reports Menu",
        "items": [
            {"id": "monthly_report", "label": "Monthly Report", "action": "command:monthly_report", "help_text": "Generate monthly financial report"},
            {"id": "category_breakdown", "label": "Category Breakdown", "action": "command:category_breakdown", "help_text": "View spending by category"},
        ]
    },
    "settings": {
        "label": "Settings Menu",
        "items": [
            {"id": "change_pin", "label": "Change PIN", "action": "command:change_pin", "help_text": "Change user PIN"},
            {"id": "update_profile", "label": "Update Profile", "action": "command:update_profile", "help_text": "Update current user's profile information"},
            {"id": "data_management", "label": "Data Management", "action": "menu:data_management", "help_text": "Export, import, or restore data"},
            {"id": "switch_account", "label": "Switch Account", "action": "command:switch_account", "help_text": "Switch to another user account"},
            {"id": "logout", "label": "Logout", "action": "command:logout", "help_text": "Log out the current user"},
        ]
    },
    "data_management": {
        "label": "Data Management",
        "items": [
            {"id": "export_data", "label": "Export Data", "action": "command:export_data", "help_text": "Export transactions to a file"},
            {"id": "import_data", "label": "Import Data", "action": "command:import_data", "help_text": "Import transactions from a file"},
            {"id": "restore_data", "label": "Restore from Backup", "action": "command:restore_data", "help_text": "Restore transactions from a backup"},
        ]
    }
}

def initialize_default_menu():
    # With hardcoded menus, this function primarily serves to ensure _ALL_MENUS is defined.
    # No dynamic initialization needed.
    pass

def get_menu_items(parent_id=None):
    menu = _ALL_MENUS.get(str(parent_id))
    if menu:
        return menu.get("items", [])
    return []

def get_menu_title(menu_id):
    menu = _ALL_MENUS.get(menu_id)
    if menu:
        return menu.get("label", "Menu")
    return "Menu"

def navigate_to_submenu(current_menu_id, target_menu_id):
    _navigation_stack.append(current_menu_id)
    return target_menu_id

def return_to_parent_menu():
    if _navigation_stack:
        return _navigation_stack.pop()
    return "main" # Fallback to main menu

def get_contextual_help(menu_id, item_id=None):
    if item_id:
        # Find the specific item's help text
        for menu_key in _ALL_MENUS:
            for item in _ALL_MENUS[menu_key].get("items", []):
                if item.get("id") == item_id:
                    return item.get("help_text")
        return "No help available for this item."
    else:
        # Return help for the current menu
        menu_items = get_menu_items(menu_id)
        help_text = f"--- Help for {get_menu_title(menu_id)} ---\n"
        for item in menu_items:
            help_text += f"- {item.get('label')}: {item.get('help_text')}\n"
        help_text += "\nQ: Exit, B: Back, H: Help"
        return help_text

def execute_command_action(action_string, transaction_manager):
    command_name = action_string.split(":")[1]
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in. Please log in first.")
        return
    user_id = current_user.username
    match command_name:
        case "add_transaction":
            add_transaction_command(transaction_manager)
        case "view_transactions":
            _handle_view_transactions(user_id, transaction_manager)
        case "edit_transaction":
            _handle_edit_transaction(transaction_manager)
        case "delete_transaction":
            _handle_delete_transaction(transaction_manager)
        case "monthly_report":
            _handle_monthly_report()
        case "category_breakdown":
            _handle_category_breakdown()
        case "change_pin":
            _handle_change_pin()
        case "update_profile":
            update_profile_command()  # Call the standalone function from src/cli/user.py
        case "switch_account":
            switch()  # Call the standalone function from src/cli/user.py
        case "logout":
            logout()  # Call the standalone function from src/cli/user.py
        case "export_data":
            _handle_export_data(transaction_manager)
        case "import_data":
            _handle_import_data(transaction_manager)
        case "restore_data":
            _handle_restore_data(transaction_manager)
        case _:
            add_message(f"Unknown command: {command_name}")

def _handle_view_transactions(user_id, transaction_manager):
    transactions = transaction_manager.get_all_transactions(user_id)
    if not transactions:
        add_message("No transactions found.", immediate=True)
    else:
        # Define column widths
        id_width = 10
        date_width = 12
        type_width = 8
        category_width = 25
        amount_width = 12
        description_width = 40 # Added description column

        header = (f"{ 'ID':<{id_width}} | { 'Date':<{date_width}} | { 'Type':<{type_width}} | "
                  f"{ 'Category':<{category_width}} | { 'Amount':>{amount_width}} | { 'Description':<{description_width}}")
        
        separator = "=" * (id_width + date_width + type_width + category_width + amount_width + description_width + (5 * 3)) # 5 for '|' and spaces

        add_message(separator, immediate=True)
        add_message(header, immediate=True)
        add_message("-" * len(header), immediate=True) # Separator under header

        for t in transactions:
            # Truncate ID for display
            display_id = str(t.id)[:id_width-3] + "..." if len(str(t.id)) > id_width else str(t.id)
            # Format amount to 2 decimal places and right-align
            formatted_amount = f"{t.currency.symbol}{t.amount:,.2f}"
            # Truncate description if too long
            display_description = t.description[:description_width] + "..." if len(t.description) > description_width else t.description

            row = (f"{display_id:<{id_width}} | {t.date:<{date_width}} | {t.type:<{type_width}} | "
                   f"{t.category:<{category_width}} | {formatted_amount:>{amount_width}} | {display_description:<{description_width}}")
            add_message(row, immediate=True)
        add_message(separator, immediate=True)

    choice = get_user_input("\nType 'e' to edit, 'd' to delete, or 'b' to go back: ").lower()
    if choice == 'e':
        _handle_edit_transaction(transaction_manager)
    elif choice == 'd':
        _handle_delete_transaction(transaction_manager)
    else:
        return

def _handle_edit_transaction(transaction_manager):
    transaction_id = get_user_input("Enter the ID of the transaction to edit: ")
    edit_transaction_command(transaction_id, transaction_manager)
    get_user_input("Press Enter to continue...")

def _handle_delete_transaction(transaction_manager):
    transaction_id = get_user_input("Enter the ID of the transaction to delete: ")
    delete_transaction_command(transaction_id, transaction_manager)
    get_user_input("Press Enter to continue...")

def _handle_monthly_report():
    add_message("Monthly report functionality not yet implemented.")
    get_user_input("Press Enter to continue...")

def _handle_category_breakdown():
    add_message("Category breakdown functionality not yet implemented.")
    get_user_input("Press Enter to continue...")

def _handle_change_pin():
    add_message("--- Change PIN ---", immediate=True)
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    old_pin = get_user_input("Enter your old PIN: ", hide_input=True)
    service = UserManagementService()
    if not service.authenticate_user(current_user.username, old_pin):
        add_message("Error: Incorrect old PIN.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    new_pin = get_user_input("Enter new PIN: ", hide_input=True)
    new_pin_confirm = get_user_input("Confirm new PIN: ", hide_input=True)

    if new_pin != new_pin_confirm:
        add_message("Error: New PINs do not match.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    is_valid, pin_msg = validate_pin(new_pin)
    if not is_valid:
        add_message(f"Error: {pin_msg}", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    if service.update_pin(current_user.username, new_pin):
        add_message("PIN changed successfully.", immediate=True)
    else:
        add_message("Error: Failed to change PIN.", immediate=True)
    get_user_input("Press Enter to continue...")

def _handle_export_data(transaction_manager):
    file_path = get_user_input("Enter the full path for the export file (e.g., /path/to/export.json): ")
    file_format = get_user_input("Enter the format (json or csv): ").lower()

    if not file_format in ['json', 'csv']:
        add_message("Invalid format. Please choose 'json' or 'csv'.")
        get_user_input("Press Enter to continue...")
        return

    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in. Please log in to export data.")
        get_user_input("Press Enter to continue...")
        return
    transactions = transaction_manager.get_all_transactions(current_user.username)
    
    success, message = transaction_manager.persistence.data_persistence_service.export_data(transactions, file_format, file_path)

    add_message(message)
    get_user_input("Press Enter to continue...")

def _handle_import_data(transaction_manager):
    file_path = get_user_input("Enter the full path for the import file (e.g., /path/to/import.json): ")
    file_format = get_user_input("Enter the format (json or csv): ").lower()

    if not file_format in ['json', 'csv']:
        add_message("Invalid format. Please choose 'json' or 'csv'.")
        get_user_input("Press Enter to continue...")
        return

    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in. Please log in to import data.")
        get_user_input("Press Enter to continue...")
        return
    success, message = transaction_manager.persistence.data_persistence_service.import_data(file_format, file_path, current_user.username)

    add_message(message)
    get_user_input("Press Enter to continue...")

def _handle_restore_data(transaction_manager):
    backups = transaction_manager.persistence.data_persistence_service.get_backups()
    if not backups:
        add_message("No backups found.")
        get_user_input("Press Enter to continue...")
        return

    add_message("Available backups:")
    for i, backup in enumerate(backups):
        add_message(f"{i+1}. {backup}")

    choice_str = get_user_input("Enter the number of the backup to restore: ")
    try:
        choice = int(choice_str)
        if not (1 <= choice <= len(backups)):
            raise ValueError()
    except ValueError:
        add_message("Invalid choice.")
        get_user_input("Press Enter to continue...")
        return

    selected_backup = backups[choice-1]
    success, message = transaction_manager.persistence.data_persistence_service.restore_from_backup(selected_backup)
    
    add_message(message)
    if success:
        # Reload transactions after restoring
        transaction_manager.persistence._load_transactions()

    get_user_input("Press Enter to continue...")