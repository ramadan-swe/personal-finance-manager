from datetime import date, datetime
from src.utils.prompt_toolkit_utils import display_menu, get_user_input, add_message, print_formatted_text
from src.utils.input_validator import validate_number, validate_iso_date, validate_type, validate_description, validate_category, validate_pin
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import get_categories, is_valid_category
from src.services.session_manager import SessionManager
from src.services.user_management import UserManagementService # Import UserManagementService
from src.cli.user import update_profile_command, switch, logout # Import user management functions
from src.services.reporting import generate_monthly_report, generate_dashboard_summary
from decimal import Decimal
import calendar

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
                {"id": "spending_trends", "label": "Spending Trends", "action": "command:spending_trends", "help_text": "View spending trends for the current month"},
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
    elif command_name == "spending_trends":
        _handle_spending_trends()
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
    add_message("--- Monthly Financial Report ---", immediate=True)
    # Prompt for year and month
    while True:
        year_str = get_user_input("Enter year (YYYY) [default: current year]: ")
        if not year_str:
            year = datetime.now().year
            break
        try:
            year = int(year_str)
            break
        except ValueError:
            add_message("Error: Invalid year. Please enter a 4-digit year.")

    while True:
        month_str = get_user_input("Enter month (1-12) [default: current month]: ")
        if not month_str:
            month = datetime.now().month
            break
        try:
            month = int(month_str)
            if 1 <= month <= 12:
                break
            else:
                add_message("Error: Month must be between 1 and 12.")
        except ValueError:
            add_message("Error: Invalid month. Enter a number between 1 and 12.")

    # Optional category filter
    categories_input = get_user_input("Enter comma-separated categories to include (leave empty for all): ")
    categories = None
    if categories_input:
        categories = [c.strip() for c in categories_input.split(",") if c.strip()]

    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user logged in.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    report = generate_monthly_report(current_user.username, year, month, categories)

    # Display report
    add_message(f"Report for {report['year']}-{report['month']:02d}", immediate=True)
    add_message(f"Total income : ${report['income']:,.2f}", immediate=True)
    add_message(f"Total expenses: ${report['expenses']:,.2f}", immediate=True)
    add_message(f"Savings       : ${report['savings']:,.2f}", immediate=True)
    add_message(f"Transactions  : {report.get('transactions_count', 0)}", immediate=True)

    # Category breakdown moved to the dedicated 'Category Breakdown' menu option
    get_user_input("Press Enter to continue...")

def _handle_category_breakdown():
    add_message("--- Category Breakdown ---", immediate=True)
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user logged in.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    # Prompt for year and month (default to current)
    while True:
        year_str = get_user_input("Enter year (YYYY) [default: current year]: ")
        if not year_str:
            year = datetime.now().year
            break
        try:
            year = int(year_str)
            break
        except ValueError:
            add_message("Error: Invalid year. Please enter a 4-digit year.")

    while True:
        month_str = get_user_input("Enter month (1-12) [default: current month]: ")
        if not month_str:
            month = datetime.now().month
            break
        try:
            month = int(month_str)
            if 1 <= month <= 12:
                break
            else:
                add_message("Error: Month must be between 1 and 12.")
        except ValueError:
            add_message("Error: Invalid month. Enter a number between 1 and 12.")

    # Generate report for the selected month and display category breakdown
    report = generate_monthly_report(current_user.username, year, month)

    add_message(f"Category breakdown for {report['year']}-{report['month']:02d}:", immediate=True)
    if not report['category_breakdown']:
        add_message("No transactions for the selected month.", immediate=True)
    else:
        # Sort categories alphabetically for stable output
        for cat in sorted(report['category_breakdown'].keys()):
            vals = report['category_breakdown'][cat]
            add_message(f"- {cat}: expenses=${vals['expenses']:,.2f}, income=${vals['income']:,.2f}, count={vals['count']}", immediate=True)

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


def _handle_spending_trends():
    add_message("--- Spending Trends (Current Month) ---", immediate=True)
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user logged in.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    now = datetime.now()
    year = now.year
    month = now.month

    # Gather expense transactions for the user in the selected month
    transactions = _transaction_manager.get_all_transactions(current_user.username)
    daily_totals = {}
    for t in transactions:
        try:
            dt = datetime.fromisoformat(t.date)
        except Exception:
            continue
        if dt.year == year and dt.month == month and t.type == 'expense':
            day = dt.day
            daily_totals[day] = daily_totals.get(day, Decimal(0)) + Decimal(str(t.amount))

    # Prepare days array
    _, days_in_month = calendar.monthrange(year, month)
    day_values = [float(daily_totals.get(d, Decimal(0))) for d in range(1, days_in_month + 1)]

    if all(v == 0 for v in day_values):
        add_message("No expense transactions for the current month.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    # Render improved fixed-width ASCII bar chart (width up to 40)
    max_val = max(day_values)
    max_bar = 40
    avg_val = sum(day_values) / len(day_values) if day_values else 0

    add_message(f"Spending trends for {now.strftime('%B %Y')} (max day: ${max_val:,.2f}, avg/day: ${avg_val:,.2f}):", immediate=True)
    add_message("".ljust(0), immediate=True)

    bar_char = '█'
    empty_char = ' '
    amount_width = 10

    # Header for bar scale
    add_message(f"    Day |{'Bar'.ljust(max_bar)}| Amount", immediate=True)
    add_message(f"    ----+{'-' * max_bar}+{'-' * (amount_width+1)}", immediate=True)

    for day, val in enumerate(day_values, start=1):
        bar_len = int((val / max_val) * max_bar) if max_val > 0 else 0
        bar = bar_char * bar_len
        empty = empty_char * (max_bar - bar_len)
        add_message(f" {day:02d}  |{bar}{empty}| ${val:>{amount_width - 1},.2f}", immediate=True)

    # Legend showing scale
    add_message("".ljust(0), immediate=True)
    add_message(f"Scale: 0 {' ' * (max_bar-6)} ${max_val:,.2f}", immediate=True)

    get_user_input("Press Enter to continue...")
