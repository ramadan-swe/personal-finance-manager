from datetime import date, datetime
from src.utils.prompt_toolkit_utils import display_menu, get_user_input, add_message, print_formatted_text
from src.utils.input_validator import validate_number, validate_currency, validate_iso_date, validate_type, validate_description, validate_category, validate_pin
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import get_categories, is_valid_category
from src.services.session_manager import SessionManager
from src.services.user_management import UserManagementService # Import UserManagementService
from src.cli.user import update_profile_command, switch, logout # Import user management functions

# Global variables for menu management
_navigation_stack = []
_transaction_manager = TransactionManager() # Initialize once globally

# Hardcoded menu structure
_ALL_MENUS = {
    "main": {
        "label": "Main Menu",
        "items": [
            {"id": "view_transactions", "label": "View Transactions", "action": "command:view_transactions", "help_text": "View all recorded transactions"},
            {"id": "search_menu", "label": "Search & Filter", "action": "menu:search_filter", "help_text": "Search and filter transactions"},
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
    "search_filter": {
        "label": "Search & Filter",
        "items": [
            {"id": "search_date_range", "label": "Search Transactions by Date Range", "action": "command:search_date_range", "help_text": "Search transactions by start and end date"},
            {"id": "filter_category", "label": "Filter Transactions by Category", "action": "command:filter_by_category", "help_text": "Show transactions for a given category"},
            {"id": "amount_range", "label": "Amount Range Filter", "action": "command:amount_range_filter", "help_text": "Filter transactions by amount range"},
        ]
    },
    "settings": {
        "label": "Settings Menu",
        "items": [
            {"id": "change_pin", "label": "Change PIN", "action": "command:change_pin", "help_text": "Change user PIN"},
            {"id": "update_profile", "label": "Update Profile", "action": "command:update_profile", "help_text": "Update current user's profile information"},
            {"id": "switch_account", "label": "Switch Account", "action": "command:switch_account", "help_text": "Switch to another user account"},
            {"id": "logout", "label": "Logout", "action": "command:logout", "help_text": "Log out the current user"},
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
        add_message("Error: No user is currently logged in. Please log in first.")
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
    elif command_name == "search_date_range":
        _handle_search_by_date_range(user_id)
    elif command_name == "filter_by_category":
        _handle_filter_by_category(user_id)
    elif command_name == "amount_range_filter":
        _handle_amount_range_filter(user_id)
    elif command_name == "change_pin":
        _handle_change_pin()
    elif command_name == "update_profile":
        update_profile_command() # Call the standalone function from src/cli/user.py
    elif command_name == "switch_account":
        switch() # Call the standalone function from src/cli/user.py
    elif command_name == "logout":
        logout() # Call the standalone function from src/cli/user.py
    else:
        add_message(f"Unknown command: {command_name}")

def _handle_add_transaction(user_id):
    add_message("--- Add New Transaction ---")
    
    while True:
        amount_str = get_user_input("Amount: ")
        is_valid, amount = validate_number(amount_str)
        if is_valid:
            break
        add_message(f"Error: {amount}")

    while True:
        date_str = get_user_input(f"Date (YYYY-MM-DD) [default: {date.today().isoformat()}]: ")
        if not date_str:
            transaction_date = date.today().isoformat()
            break
        is_valid, transaction_date = validate_iso_date(date_str)
        if is_valid:
            break
        add_message(f"Error: {transaction_date}")
    
    while True:
        type_str = get_user_input("Type (income/expense): ")
        is_valid, transaction_type = validate_type(type_str)
        if is_valid:
            break
        add_message(f"Error: {transaction_type}")

    while True:
        description = get_user_input("Description: ")
        is_valid, description = validate_description(description)
        if is_valid:
            break
        add_message(f"Error: {description}")

    while True:
        categories = get_categories()
        add_message(f"Available Categories: {', '.join(categories)}", immediate=True)
        category = get_user_input("Category (leave empty for 'Uncategorized'): ")
        if not category:
            category = "Uncategorized"
            break
        is_valid, category_error = validate_category(category)
        if not is_valid:
            add_message(f"Error: {category_error}")
            continue
        if not is_valid_category(category):
            add_message(f"Error: Invalid category '{category}'")
            continue
        break

    if _transaction_manager.add_transaction(amount, transaction_date, transaction_type, description, category, user_id):
        add_message("Transaction added successfully.")
    else:
        add_message("Failed to add transaction.")
    get_user_input("Press Enter to continue...")

def _handle_view_transactions(user_id):
    transactions = _transaction_manager.get_all_transactions(user_id)
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

        header = (f"{'ID':<{id_width}} | {'Date':<{date_width}} | {'Type':<{type_width}} | "
                  f"{'Category':<{category_width}} | {'Amount':>{amount_width}} | {'Description':<{description_width}}")
        
        separator = "=" * (id_width + date_width + type_width + category_width + amount_width + description_width + (5 * 3)) # 5 for '|' and spaces

        add_message(separator, immediate=True)
        add_message(header, immediate=True)
        add_message("-" * len(header), immediate=True) # Separator under header

        for t in transactions:
            # Truncate ID for display
            display_id = t.id[:id_width-3] + "..." if len(t.id) > id_width else t.id
            # Format amount to 2 decimal places and right-align
            formatted_amount = f"${t.amount:,.2f}"
            # Truncate description if too long
            display_description = t.description[:description_width] + "..." if len(t.description) > description_width else t.description

            row = (f"{display_id:<{id_width}} | {t.date:<{date_width}} | {t.type:<{type_width}} | "
                   f"{t.category:<{category_width}} | {formatted_amount:>{amount_width}} | {display_description:<{description_width}}")
            add_message(row, immediate=True)
        add_message(separator, immediate=True)
    get_user_input("Press Enter to continue...")

def _handle_monthly_report():
    add_message("Monthly report functionality not yet implemented.")
    get_user_input("Press Enter to continue...")

def _handle_category_breakdown():
    add_message("Category breakdown functionality not yet implemented.")
    get_user_input("Press Enter to continue...")


def _handle_search_by_date_range(user_id):
    add_message("--- Search Transactions by Date Range ---")
    # Prompt for start date
    while True:
        start_str = get_user_input("Start date (YYYY-MM-DD): ")
        is_valid, start_date_str = validate_iso_date(start_str)
        if is_valid:
            try:
                start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                break
            except Exception:
                add_message("Error: Invalid start date format.")
                continue
        add_message(f"Error: {start_date_str}")

    # Prompt for end date
    while True:
        end_str = get_user_input("End date (YYYY-MM-DD): ")
        is_valid, end_date_str = validate_iso_date(end_str)
        if is_valid:
            try:
                end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except Exception:
                add_message("Error: Invalid end date format.")
                continue
            # Validate range
            if end_dt < start_dt:
                add_message("Error: End date must be the same or after start date.")
                continue
            break
        add_message(f"Error: {end_date_str}")

    transactions = _transaction_manager.get_all_transactions(user_id)
    # Filter by inclusive date range
    matched = []
    for t in transactions:
        try:
            t_dt = datetime.strptime(t.date, "%Y-%m-%d").date()
        except Exception:
            # Skip malformed dates
            continue
        if start_dt <= t_dt <= end_dt:
            matched.append(t)

    if not matched:
        add_message("No transactions found in that date range.", immediate=True)
    else:
        # Sort by date ascending
        matched.sort(key=lambda x: x.date)
        add_message(f"Found {len(matched)} transaction(s) between {start_dt} and {end_dt}.", immediate=True)
        _display_transactions_table(matched)

    get_user_input("Press Enter to continue...")


def _handle_filter_by_category(user_id):
    add_message("--- Filter Transactions by Category ---")
    categories = get_categories()
    add_message(f"Available categories: {', '.join(categories)}", immediate=True)
    add_message("You may enter multiple categories separated by commas (e.g. Food,Transport). Leave empty to show 'Uncategorized'.", immediate=True)

    while True:
        categories_input = get_user_input("Enter category or categories: ")
        if not categories_input:
            selected = ["Uncategorized"]
            break
        # Parse comma-separated list
        parts = [p.strip() for p in categories_input.split(',') if p.strip()]
        if not parts:
            add_message("Please enter at least one category or leave empty for 'Uncategorized'.")
            continue

        # Build mapping for case-insensitive match
        canonical = {c.lower(): c for c in categories}
        resolved = []
        invalid = []
        for p in parts:
            low = p.lower()
            if low in canonical:
                resolved.append(canonical[low])
            elif p == "Uncategorized":
                resolved.append("Uncategorized")
            else:
                invalid.append(p)

        if invalid:
            add_message(f"Invalid categories: {', '.join(invalid)}. Please choose from available categories.")
            continue

        selected = list(dict.fromkeys(resolved))
        break

    transactions = _transaction_manager.get_all_transactions(user_id)
    matched = [t for t in transactions if t.category in selected]
    if not matched:
        add_message(f"No transactions found for category(ies) '{', '.join(selected)}'.", immediate=True)
    else:
        add_message(f"Found {len(matched)} transaction(s) for category(ies): {', '.join(selected)}", immediate=True)
        _display_transactions_table(matched)
    get_user_input("Press Enter to continue...")


def _handle_amount_range_filter(user_id):
    from decimal import Decimal, InvalidOperation

    add_message("--- Amount Range Filter ---")
    add_message("You can enter amounts like 12.34 or $12.34. Leave blank to cancel.", immediate=True)

    # Prompt for minimum amount
    while True:
        min_str = get_user_input("Minimum amount: ")
        if not min_str:
            add_message("Amount range filter cancelled.")
            return
        # Try numeric then currency validator
        is_valid_num, num_val = validate_number(min_str)
        if is_valid_num:
            try:
                min_val = Decimal(str(float(num_val)))
                break
            except Exception:
                add_message(f"Error: Invalid minimum amount ('{min_str}'). Please enter a numeric value.")
                continue

        is_valid_cur, cur_val = validate_currency(min_str)
        if is_valid_cur:
            try:
                min_val = Decimal(str(float(cur_val)))
                break
            except Exception:
                add_message(f"Error: Invalid minimum amount ('{min_str}'). Please enter a numeric value.")
                continue

        # Neither validator passed
        add_message(f"Error: Invalid minimum amount ('{min_str}'). Please enter a numeric value (e.g., 12.34 or $12.34).")

    # Prompt for maximum amount
    while True:
        max_str = get_user_input("Maximum amount: ")
        if not max_str:
            add_message("Amount range filter cancelled.")
            return
        is_valid_num, num_val = validate_number(max_str)
        if is_valid_num:
            try:
                max_val = Decimal(str(float(num_val)))
            except Exception:
                add_message(f"Error: Invalid maximum amount ('{max_str}'). Please enter a numeric value.")
                continue
        else:
            is_valid_cur, cur_val = validate_currency(max_str)
            if is_valid_cur:
                try:
                    max_val = Decimal(str(float(cur_val)))
                except Exception:
                    add_message(f"Error: Invalid maximum amount ('{max_str}'). Please enter a numeric value.")
                    continue
            else:
                add_message(f"Error: Invalid maximum amount ('{max_str}'). Please enter a numeric value (e.g., 12.34 or $12.34).")
                continue

        if max_val < min_val:
            add_message("Error: Maximum amount must be greater than or equal to minimum amount.")
            continue
        break

    transactions = _transaction_manager.get_all_transactions(user_id)
    matched = []
    for t in transactions:
        try:
            amt = Decimal(str(t.amount))
        except Exception:
            continue
        if min_val <= amt <= max_val:
            matched.append(t)

    if not matched:
        add_message("No transactions found in that amount range.", immediate=True)
    else:
        # sort by amount ascending
        matched.sort(key=lambda x: float(x.amount))
        add_message(f"Found {len(matched)} transaction(s) in amount range ${min_val:,.2f} - ${max_val:,.2f}", immediate=True)
        _display_transactions_table(matched)
    get_user_input("Press Enter to continue...")


def _display_transactions_table(transactions):
    # Reuse the same table formatting as _handle_view_transactions
    id_width = 10
    date_width = 12
    type_width = 8
    category_width = 25
    amount_width = 12
    description_width = 40

    header = (f"{'ID':<{id_width}} | {'Date':<{date_width}} | {'Type':<{type_width}} | "
              f"{'Category':<{category_width}} | {'Amount':>{amount_width}} | {'Description':<{description_width}}")
    separator = "=" * (id_width + date_width + type_width + category_width + amount_width + description_width + (5 * 3))

    add_message(separator, immediate=True)
    add_message(header, immediate=True)
    add_message("-" * len(header), immediate=True)

    for t in transactions:
        display_id = t.id[:id_width-3] + "..." if len(t.id) > id_width else t.id
        formatted_amount = f"${t.amount:,.2f}"
        display_description = t.description[:description_width] + "..." if len(t.description) > description_width else t.description
        row = (f"{display_id:<{id_width}} | {t.date:<{date_width}} | {t.type:<{type_width}} | "
               f"{t.category:<{category_width}} | {formatted_amount:>{amount_width}} | {display_description:<{description_width}}")
        add_message(row, immediate=True)
    add_message(separator, immediate=True)

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
