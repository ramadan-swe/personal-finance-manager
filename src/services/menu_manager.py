from datetime import date, datetime, datetime
from src.utils.prompt_toolkit_utils import display_menu, get_user_input, add_message, print_formatted_text
from src.utils.input_validator import validate_number, validate_currency, validate_iso_date, validate_type, validate_description, validate_category, validate_pin
import json
from decimal import Decimal, InvalidOperation
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import get_categories, is_valid_category
from src.services.session_manager import SessionManager
from src.services.user_management import UserManagementService
from src.services.data_persistence import DataPersistenceService
from src.cli.user import update_profile_command, switch, logout
from src.cli.transaction import add_transaction_command, edit_transaction_command, delete_transaction_command
from src.services.reporting import generate_monthly_report, generate_dashboard_summary
from src.models.transaction import PaymentMethod, Currencies
from decimal import Decimal
import calendar

# Global variables for menu management
_navigation_stack = []

# Hardcoded menu structure
_ALL_MENUS = {
    "main": {
        "label": "Main Menu",
        "items": [
            {"id": "view_transactions", "label": "View Transactions", "action": "command:view_transactions", "help_text": "View all recorded transactions"},
            {"id": "search_menu", "label": "Search & Filter", "action": "menu:search_filter", "help_text": "Search and filter transactions"},
            {"id": "add_transaction", "label": "Add Transaction", "action": "command:add_transaction", "help_text": "Add a new financial transaction"},
            {"id": "reports_menu", "label": "Reports", "action": "menu:reports", "help_text": "Access financial reports"},
            {"id": "savings_menu", "label": "Saving goal", "action": "menu:savings", "help_text": "Manage saving goals"},
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
    "search_filter": {
        "label": "Search & Filter",
        "items": [
            {"id": "search_date_range", "label": "Search Transactions by Date Range", "action": "command:search_date_range", "help_text": "Search transactions by start and end date"},
            {"id": "filter_category", "label": "Filter Transactions by Category", "action": "command:filter_by_category", "help_text": "Show transactions for a given category"},
            {"id": "amount_range", "label": "Amount Range Filter", "action": "command:amount_range_filter", "help_text": "Filter transactions by amount range"},
        ]
    },
    "savings": {
        "label": "Saving Goals",
        "items": [
            {"id": "set_saving_goal", "label": "Set Saving Goal", "action": "command:set_saving_goal", "help_text": "Create or update a saving goal"},
            {"id": "view_saving_goals", "label": "View & Add Saving Goals", "action": "command:view_saving_goals", "help_text": "View existing saving goals and add new ones"},
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
        case "set_saving_goal":
            _handle_set_saving_goal(user_id)
        case "view_saving_goals":
            _handle_view_saving_goals(user_id)
        case "spending_trends":
            _handle_spending_trends(transaction_manager)
        case "search_date_range":
            _handle_search_by_date_range(user_id, transaction_manager)
        case "filter_by_category":
            _handle_filter_by_category(user_id, transaction_manager)
        case "amount_range_filter":
            _handle_amount_range_filter(user_id, transaction_manager)
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


def _handle_search_by_date_range(user_id, transaction_manager):
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

    transactions = transaction_manager.get_all_transactions(user_id)
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


def _handle_filter_by_category(user_id, transaction_manager):
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

    transactions = transaction_manager.get_all_transactions(user_id)
    matched = [t for t in transactions if t.category in selected]
    if not matched:
        add_message(f"No transactions found for category(ies) '{', '.join(selected)}'.", immediate=True)
    else:
        add_message(f"Found {len(matched)} transaction(s) for category(ies): {', '.join(selected)}", immediate=True)
        _display_transactions_table(matched)
    get_user_input("Press Enter to continue...")


def _handle_amount_range_filter(user_id, transaction_manager):
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

    transactions = transaction_manager.get_all_transactions(user_id)
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
        display_id = str(t.id)[:id_width-3] + "..." if len(str(t.id)) > id_width else str(t.id)
        formatted_amount = f"{getattr(t, 'currency', type('C', (), {'symbol': '$'})) .symbol}{t.amount:,.2f}"
        display_description = t.description[:description_width] + "..." if len(t.description) > description_width else t.description
        row = (f"{display_id:<{id_width}} | {t.date:<{date_width}} | {t.type:<{type_width}} | "
               f"{t.category:<{category_width}} | {formatted_amount:>{amount_width}} | {display_description:<{description_width}}")
        add_message(row, immediate=True)
    add_message(separator, immediate=True)


### Savings goal handlers & simple persistence
_SAVINGS_FILE = "savings.json"


def _load_savings():
    try:
        with open(_SAVINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def _save_savings(data):
    try:
        with open(_SAVINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def _handle_set_saving_goal(user_id):
    add_message("--- Set Saving Goal ---")
    name = get_user_input("Goal name (e.g. Emergency Fund): ").strip()
    if not name:
        add_message("Goal name cannot be empty.")
        return

    # amount
    while True:
        amount_str = get_user_input("Target amount: ")
        is_valid, amt = validate_number(amount_str)
        if is_valid:
            try:
                amount = float(amt)
                break
            except Exception:
                add_message("Invalid amount. Try again.")
                continue
        else:
            add_message(f"Error: {amt}")

    # optional target date
    target_date = get_user_input("Target date (YYYY-MM-DD) [optional]: ")
    if target_date:
        ok, msg = validate_iso_date(target_date)
        if not ok:
            add_message(f"Warning: target date invalid ({msg}). Saving without date.")
            target_date = ""

    # Load existing
    data = _load_savings()
    user_goals = data.get(user_id, [])

    # Replace if same name exists
    for g in user_goals:
        if g.get('name') == name:
            g['amount'] = amount
            g['target_date'] = target_date
            break
    else:
        user_goals.append({'name': name, 'amount': amount, 'target_date': target_date})

    data[user_id] = user_goals
    if _save_savings(data):
        add_message("Saving goal saved successfully.", immediate=True)
    else:
        add_message("Failed to save saving goal.", immediate=True)
    get_user_input("Press Enter to continue...")


def _handle_view_saving_goals(user_id):
    add_message("--- Your Saving Goals ---")
    data = _load_savings()
    user_goals = data.get(user_id, [])
    if not user_goals:
        add_message("No saving goals found.", immediate=True)
        get_user_input("Press Enter to continue...")
        return

    # display
    # Fetch user's transactions to compute progress towards goals
    try:
        tm = TransactionManager(DataPersistenceService())
        transactions = tm.get_all_transactions(user_id)
    except Exception:
        transactions = []

    for idx, g in enumerate(user_goals, start=1):
        goal_name = str(g.get('name', '')).strip()
        target_amount = g.get('amount', 0) or 0
        td = g.get('target_date', '')

        # Compute saved amount: match transactions where category equals goal name (case-insensitive),
        # or category == 'Savings', or description contains the goal name. This is an assumption.
        saved = Decimal(0)
        if transactions and goal_name:
            for t in transactions:
                try:
                    amt = Decimal(str(t.amount))
                except Exception:
                    continue
                cat = (t.category or '')
                desc = (t.description or '')
                if (cat and cat.lower() == goal_name.lower()) or (cat and cat.lower() == 'savings') or (goal_name.lower() in desc.lower()):
                    saved += amt

        # Prepare progress display
        try:
            target_dec = Decimal(str(target_amount))
        except Exception:
            target_dec = Decimal(0)

        percent = Decimal(0)
        remaining = Decimal(0)
        if target_dec > 0:
            percent = (saved / target_dec) * Decimal(100)
            if percent > 100:
                percent = Decimal(100)
            remaining = target_dec - saved
            if remaining < 0:
                remaining = Decimal(0)

        # Render a small progress bar (width 30)
        bar_width = 30
        filled = 0
        try:
            filled = int((float(percent) / 100.0) * bar_width) if target_dec > 0 else 0
        except Exception:
            filled = 0

        bar = '█' * filled + '-' * (bar_width - filled)

        add_message(f"{idx}. {goal_name}: target=${target_dec:,.2f} {'by '+td if td else ''}", immediate=True)
        add_message(f"    Progress: |{bar}| {float(percent):.2f}%  saved=${saved:,.2f} remaining=${remaining:,.2f}", immediate=True)

    # Offer quick action: enter a goal number to add money, or 'a' to add a new goal
    choice = get_user_input("\nEnter goal number to add money, 'a' to add a new saving goal, or press Enter to return: ").strip().lower()
    if not choice:
        return
    if choice == 'a':
        _handle_set_saving_goal(user_id)
        return

    # If numeric, delegate to the centralized add-to-goal handler (preselected goal)
    try:
        sel_index = int(choice) - 1
        _handle_add_to_saving_goal(user_id, transactions, selected_index=sel_index)
    except Exception:
        add_message("Invalid input.", immediate=True)
    return

def _handle_add_to_saving_goal(user_id, transactions=None, selected_index=None):
    """Interactive flow to add a contribution to an existing saving goal.

    This function computes net saving (income - expenses), prompts the user to
    pick a goal by number or add a new goal, validates contribution amount
    against available net saving, and records the contribution as an expense
    transaction categorized by the goal name.
    """
    # Load transactions if not provided
    if transactions is None:
        try:
            tm = TransactionManager(DataPersistenceService())
            transactions = tm.get_all_transactions(user_id)
        except Exception:
            transactions = []

    # Load goals
    data = _load_savings()
    user_goals = data.get(user_id, [])
    if not user_goals:
        add_message("No saving goals found.", immediate=True)
        return

    # Compute net saving
    net_saving = Decimal(0)
    total_income = Decimal(0)
    total_expenses = Decimal(0)
    for t in transactions:
        try:
            amt = Decimal(str(t.amount))
        except Exception:
            continue
        if getattr(t, 'type', '') == 'income':
            total_income += amt
        else:
            total_expenses += amt
    net_saving = total_income - total_expenses

    add_message("")
    add_message(f"Net available saving: ${net_saving:,.2f}", immediate=True)

    if selected_index is None:
        choice = get_user_input("\nEnter goal number to add money, 'a' to add a new goal, or press Enter to cancel: ").strip().lower()
        if not choice:
            return
        if choice == 'a':
            _handle_set_saving_goal(user_id)
            return
        try:
            sel = int(choice)
            if sel < 1 or sel > len(user_goals):
                add_message("Invalid selection.", immediate=True)
                return
            selected_index = sel - 1
        except Exception:
            add_message("Invalid input.", immediate=True)
            return

    if selected_index < 0 or selected_index >= len(user_goals):
        add_message("Invalid selection.", immediate=True)
        return

    selected_goal = user_goals[selected_index]
    goal_name = str(selected_goal.get('name', '')).strip()

    # Prompt for contribution amount
    while True:
        amt_str = get_user_input(f"Enter amount to add to '{goal_name}' (or leave blank to cancel): ")
        if not amt_str:
            add_message("Add-to-goal cancelled.", immediate=True)
            return
        is_num, num_val = validate_number(amt_str)
        if is_num:
            try:
                contrib = Decimal(str(float(num_val)))
            except Exception:
                add_message("Invalid amount. Try again.")
                continue
        else:
            is_cur, cur_val = validate_currency(amt_str)
            if is_cur:
                try:
                    contrib = Decimal(str(float(cur_val)))
                except Exception:
                    add_message("Invalid amount. Try again.")
                    continue
            else:
                add_message("Invalid amount format. Use numbers like 12.34 or $12.34.")
                continue

        if contrib <= Decimal(0):
            add_message("Amount must be positive.", immediate=True)
            continue
        if contrib > net_saving:
            add_message(f"Insufficient net saving. You have ${net_saving:,.2f} available.", immediate=True)
            retry = get_user_input("Type 'y' to retry with a smaller amount or press Enter to cancel: ").strip().lower()
            if retry == 'y':
                continue
            return

        # Record contribution as an expense transaction categorized by the goal name
        today_str = datetime.now().strftime('%Y-%m-%d')
        tm2 = TransactionManager(DataPersistenceService())
        description = f"Contribution to goal: {goal_name}"
        # Use proper enum/object types to ensure persistence works
        payment_method_default = PaymentMethod.DEBIT
        currency_default = Currencies.USD
        try:
            ok = tm2.add_transaction(float(contrib), today_str, 'expense', description, goal_name, user_id, payment_method_default, currency_default)
        except Exception as e:
            add_message(f"Error recording contribution: {e}", immediate=True)
            return

        if not ok:
            add_message("Failed to record contribution as a transaction.", immediate=True)
            return

        # Refresh transactions and recompute saved/net saving to show updated state
        try:
            transactions = tm2.get_all_transactions(user_id)
        except Exception:
            transactions = []

        # recompute saved for the selected goal
        new_saved = Decimal(0)
        for t in transactions:
            try:
                amt = Decimal(str(t.amount))
            except Exception:
                continue
            cat = (t.category or '')
            desc = (t.description or '')
            if (cat and cat.lower() == goal_name.lower()) or (cat and cat.lower() == 'savings') or (goal_name.lower() in desc.lower()):
                new_saved += amt

        # recompute net saving
        total_income = Decimal(0)
        total_expenses = Decimal(0)
        for t in transactions:
            try:
                amt = Decimal(str(t.amount))
            except Exception:
                continue
            if getattr(t, 'type', '') == 'income':
                total_income += amt
            else:
                total_expenses += amt
        new_net = total_income - total_expenses

        add_message(f"Added ${contrib:,.2f} to '{goal_name}'. New saved=${new_saved:,.2f}, Net available saving=${new_net:,.2f}", immediate=True)
        return

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

def _handle_spending_trends(transaction_manager):
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
    transactions = transaction_manager.get_all_transactions(current_user.username)
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
