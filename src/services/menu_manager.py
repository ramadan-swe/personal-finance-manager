from datetime import date
from src.utils.prompt_toolkit_utils import display_menu, get_user_input
from src.utils.input_validator import validate_number, validate_iso_date, validate_type, validate_description, validate_category
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import get_categories, is_valid_category
from src.services.session_manager import SessionManager

# Global variables for menu management
_navigation_stack = []
_transaction_manager = TransactionManager() # Initialize once globally

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

def execute_command_action(action_string):
    command_name = action_string.split(":")[1]
    current_user = SessionManager.get_current_user()
    if not current_user:
        print("Error: No user is currently logged in. Please log in first.")
        return
    user_id = current_user.username
    if command_name == "add_transaction":
        _handle_add_transaction(user_id)
    elif command_name == "view_transactions":
        _handle_view_transactions(user_id)
    elif command_name == "monthly_report":
        _handle_monthly_report()
    elif command_name == "category_breakdown":
        _handle_category_breakdown()
    elif command_name == "change_pin":
        _handle_change_pin()
    else:
        print(f"Unknown command: {command_name}")

def _handle_add_transaction(user_id):
    print("--- Add New Transaction ---")
    
    while True:
        amount_str = get_user_input("Amount: ")
        is_valid, amount = validate_number(amount_str)
        if is_valid:
            break
        print(f"Error: {amount}")

    while True:
        date_str = get_user_input(f"Date (YYYY-MM-DD) [default: {date.today().isoformat()}]: ")
        if not date_str:
            transaction_date = date.today().isoformat()
            break
        is_valid, transaction_date = validate_iso_date(date_str)
        if is_valid:
            break
        print(f"Error: {transaction_date}")
    
    while True:
        type_str = get_user_input("Type (income/expense): ")
        is_valid, transaction_type = validate_type(type_str)
        if is_valid:
            break
        print(f"Error: {transaction_type}")

    while True:
        description = get_user_input("Description: ")
        is_valid, description = validate_description(description)
        if is_valid:
            break
        print(f"Error: {description}")

    while True:
        categories = get_categories()
        print(f"Available Categories: {', '.join(categories)}")
        category = get_user_input("Category (leave empty for 'Uncategorized'): ")
        if not category:
            category = "Uncategorized"
            break
        is_valid, category_error = validate_category(category)
        if not is_valid:
            print(f"Error: {category_error}")
            continue
        if not is_valid_category(category):
            print(f"Error: Invalid category '{category}'")
            continue
        break

    if _transaction_manager.add_transaction(amount, transaction_date, transaction_type, description, category, user_id):
        print("Transaction added successfully.")
    else:
        print("Failed to add transaction.")
    get_user_input("Press Enter to continue...")

def _handle_view_transactions(user_id):
    print("--- View Transactions ---")
    transactions = _transaction_manager.get_all_transactions(user_id)
    if not transactions:
        print("No transactions found.")
    else:
        for t in transactions:
            print(f"ID: {t.id[:8]}..., Amount: {t.amount}, Date: {t.date}, Type: {t.type}, Desc: {t.description}, Cat: {t.category}")
    get_user_input("Press Enter to continue...")

def _handle_monthly_report():
    print("Monthly report functionality not yet implemented.")
    get_user_input("Press Enter to continue...")

def _handle_category_breakdown():
    print("Category breakdown functionality not yet implemented.")
    get_user_input("Press Enter to continue...")

def _handle_change_pin():
    print("Change PIN functionality not yet implemented.")
    get_user_input("Press Enter to continue...")
