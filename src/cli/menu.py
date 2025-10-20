from src.services.menu_manager import get_menu_items, get_menu_title, navigate_to_submenu, return_to_parent_menu, get_contextual_help, execute_command_action, initialize_default_menu
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input, display_menu, add_message
from src.utils.input_validator import validate_integer
from src.services.reporting import generate_monthly_report, generate_dashboard_summary
from datetime import datetime
from src.services.transaction_manager import TransactionManager
from decimal import Decimal, getcontext

getcontext().prec = 28


def _render_dashboard_box_lines(user_display: str, period_display: str, total_income: float, total_expenses: float, net_savings: float, current_balance: float, top_categories: list):
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

def start():
    """Starts the main hierarchical menu."""
    initialize_default_menu() # Initialize menu items
    current_menu_id = "main"
    # user_id is no longer directly used for menu navigation state, but still needed for SessionManager
    # user_id = SessionManager.get_current_user().username 
    while True:
        menu_items = get_menu_items(current_menu_id)
        if not menu_items:
            print("No menu items found.")
            break
        
        # If showing main menu and user is logged in, render ASCII dashboard box above menu
        if current_menu_id == "main" and SessionManager.is_logged_in():
            try:
                current_user = SessionManager.get_current_user()
                now = datetime.now()
                monthly = generate_monthly_report(current_user.username, now.year, now.month)

                # Compute current balance from all transactions
                tm = TransactionManager()
                all_tx = tm.get_all_transactions(current_user.username)
                balance = Decimal(0)
                for t in all_tx:
                    amt = Decimal(str(t.amount))
                    if t.type == 'income':
                        balance += amt
                    else:
                        balance -= amt

                # Prepare top categories (percent relative to monthly expenses)
                breakdown = monthly.get('category_breakdown', {})
                total_exp = Decimal(str(monthly.get('expenses', 0)))
                cats = []
                for cat, vals in breakdown.items():
                    exp_amt = Decimal(str(vals.get('expenses', 0)))
                    pct = (exp_amt / total_exp * 100) if total_exp > 0 else Decimal(0)
                    cats.append({'category': cat, 'amount': float(exp_amt), 'percent': float(pct)})
                cats_sorted = sorted(cats, key=lambda x: x['amount'], reverse=True)[:3]

                box_lines = _render_dashboard_box_lines(current_user.username, now.strftime('%B %Y'), monthly.get('income', 0.0), monthly.get('expenses', 0.0), monthly.get('savings', 0.0), float(balance), cats_sorted)
                for ln in box_lines:
                    add_message(ln)
            except Exception:
                pass

        # Display the menu using the utility function
        menu_title = get_menu_title(current_menu_id)
        display_menu(menu_title, menu_items)

        choice = get_user_input("Enter your choice: ").strip().upper()

        if choice == 'Q':
            break
        elif choice == 'B' and current_menu_id != "main":
            current_menu_id = return_to_parent_menu()
        elif choice == 'H': # Added for help command
            print(get_contextual_help(current_menu_id))
        else:
            is_valid, validated_choice = validate_integer(choice, min_val=1, max_val=len(menu_items))
            if is_valid:
                selected_item = menu_items[int(validated_choice) - 1]
                if selected_item.get("action").startswith("menu:"):
                    current_menu_id = navigate_to_submenu(current_menu_id, selected_item.get("action").split(":")[1])
                elif selected_item.get("action").startswith("command:"):
                    execute_command_action(selected_item.get("action"))
                else:
                    print(f"Unknown action type: {selected_item.get('action')}")
            else:
                print(f"Invalid input: {validated_choice}. Please enter a number, 'Q', 'B', or 'H'.")