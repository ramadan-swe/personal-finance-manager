from src.services.menu_manager import get_menu_items, get_menu_title, navigate_to_submenu, return_to_parent_menu, get_contextual_help, execute_command_action
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input, display_menu, add_message
from src.utils.input_validator import validate_integer
from src.services.reporting import generate_monthly_report, generate_financial_health_score
from datetime import datetime

from decimal import Decimal, getcontext

# Setting precision for Decimal calculations
getcontext().prec = 28


def _render_dashboard_box_lines(user_display: str, period_display: str, total_income: float, total_expenses: float, net_savings: float, current_balance: float, top_categories: list, financial_health: dict):
    # Build content lines similar to project sample
    lines = []
    lines.append(f"User: {user_display}")
    lines.append(f"Period: {period_display}")
    lines.append("")
    lines.append(f"Total Income:        ${total_income:,.2f}")
    lines.append(f"Total Expenses:      ${total_expenses:,.2f}")
    lines.append(f"Net Savings:         ${net_savings:,.2f}")
    lines.append("")
    lines.append(f"Current Balance:     ${current_balance:,.2f}")
    lines.append("")
    lines.append(f"Health Score:        {financial_health.get('financial_health_score', 0.0):.2f} ({financial_health.get('status', 'N/A')})")

    title = "PERSONAL FINANCE MANAGER v1.0"
    content_width = max(len(title), *(len(l) for l in lines))
    box_width = content_width + 2

    out = []
    out.append(f"┌{'─' * box_width}┐")
    out.append(f"│{title.center(box_width)}│")
    out.append(f"├{'─' * box_width}┤")
    for l in lines:
        out.append(f"│{l.ljust(box_width)}│")
    out.append(f"└{'─' * box_width}┘")

    # Top categories block
    out.append("")
    out.append("Top Spending Categories:")
    for idx, item in enumerate(top_categories, start=1):
        out.append(f"{idx}. {item['category']:<20} ${item['amount']:>8,.2f}   ({item['percent']:>4.1f}%)")

    return out

def _should_render_dashboard(current_menu_id):
    """Check if dashboard should be rendered."""
    return current_menu_id == "main" and SessionManager.is_logged_in()

def _compute_current_balance(transaction_manager, username):
    """Compute current balance from all transactions."""
    all_tx = transaction_manager.get_all_transactions(username)
    balance = Decimal(0)
    for t in all_tx:
        amt = Decimal(str(t.amount))
        if t.type == 'income':
            balance += amt
        else:
            balance -= amt
    return balance

def _prepare_top_categories(monthly_report):
    """Prepare top spending categories data."""
    breakdown = monthly_report.get('category_breakdown', {})
    total_exp = Decimal(str(monthly_report.get('expenses', 0)))
    cats = []
    for cat, vals in breakdown.items():
        exp_amt = Decimal(str(vals.get('expenses', 0)))
        pct = (exp_amt / total_exp * 100) if total_exp > 0 else Decimal(0)
        cats.append({'category': cat, 'amount': float(exp_amt), 'percent': float(pct)})
    return sorted(cats, key=lambda x: x['amount'], reverse=True)[:3]

def _render_dashboard_if_needed(current_menu_id, transaction_manager):
    """
    Renders the dashboard if on main menu and user is logged in.
    """
    if not _should_render_dashboard(current_menu_id):
        return

    try:
        current_user = SessionManager.get_current_user()
        if not current_user:
            add_message("Error: No user logged in for dashboard summary.", immediate=True)
            return

        now = datetime.now()
        monthly = generate_monthly_report(current_user.username, now.year, now.month)
        financial_health = generate_financial_health_score(current_user.username)
        balance = _compute_current_balance(transaction_manager, current_user.username)
        top_categories = _prepare_top_categories(monthly)

        box_lines = _render_dashboard_box_lines(
            current_user.username, now.strftime('%B %Y'),
            monthly.get('income', 0.0), monthly.get('expenses', 0.0),
            monthly.get('savings', 0.0), float(balance),
            top_categories, financial_health
        )
        for ln in box_lines:
            add_message(ln)
    except Exception:
        pass

def _display_menu_and_get_choice(menu_title, menu_items):
    """
    Displays the menu and gets user choice.
    """
    display_menu(menu_title, menu_items)
    return get_user_input("Enter your choice: ").strip().upper()

def _process_choice(choice, current_menu_id, menu_items, transaction_manager):
    """
    Processes the user's menu choice and returns the new menu ID or None to exit.
    """
    if choice == 'Q':
        return None
    elif choice == 'B' and current_menu_id != "main":
        return return_to_parent_menu()
    elif choice == 'H': # Added for help command
        add_message(get_contextual_help(current_menu_id))
        return current_menu_id
    else:
        is_valid, validated_choice = validate_integer(choice, min_val=1, max_val=len(menu_items))
        if is_valid:
            selected_item = menu_items[int(validated_choice) - 1]
            if selected_item.get("action").startswith("menu:"):
                return navigate_to_submenu(current_menu_id, selected_item.get("action").split(":")[1])
            elif selected_item.get("action").startswith("command:"):
                execute_command_action(selected_item.get("action"), transaction_manager)
                return current_menu_id
            else:
                add_message(f"Unknown action type: {selected_item.get("action")}")
                return current_menu_id
        else:
            add_message(f"Invalid input: {validated_choice}. Please enter a number, 'Q', 'B', or 'H'.")
            return current_menu_id

def start(transaction_manager):
    """Starts the main hierarchical menu."""
    current_menu_id = "main"
    # user_id is no longer directly used for menu navigation state, but still needed for SessionManager
    # user_id = SessionManager.get_current_user().username 
    while True:
        menu_items = get_menu_items(current_menu_id)
        if not menu_items:
            add_message("No menu items found.")
            break
        
        _render_dashboard_if_needed(current_menu_id, transaction_manager)

        menu_title = get_menu_title(current_menu_id)
        choice = _display_menu_and_get_choice(menu_title, menu_items)

        new_menu_id = _process_choice(choice, current_menu_id, menu_items, transaction_manager)
        if new_menu_id is None:
            break
        current_menu_id = new_menu_id