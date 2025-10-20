from src.cli.menu import start
from src.cli.user import register, login
from src.models.user_account import UserAccountPersistence
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input

from src.utils.prompt_toolkit_utils import get_user_input, clear_screen, add_message, display_messages
from src.services.reporting import generate_dashboard_summary, generate_monthly_report
from src.services.transaction_manager import TransactionManager
from datetime import datetime
from decimal import Decimal, getcontext

getcontext().prec = 28


def _render_dashboard_box(user_display: str, period_display: str, total_income: float, total_expenses: float, net_savings: float, current_balance: float, top_categories: list):
    """Return a list of lines representing an ASCII dashboard box."""
    # Prepare content lines
    lines = []
    lines.append(f"User: {user_display}")
    lines.append(f"Period: {period_display}")
    lines.append("")
    lines.append(f"Total Income:        ${total_income:,.2f}")
    lines.append(f"Total Expenses:      ${total_expenses:,.2f}")
    lines.append(f"Net Savings:         ${net_savings:,.2f}")
    lines.append("")
    lines.append(f"Current Balance:     ${current_balance:,.2f}")

    # Determine box width based on longest line
    content_width = max(len(l) for l in lines)
    title = "PERSONAL FINANCE MANAGER v1.0"
    content_width = max(content_width, len(title))
    box_width = content_width + 4

    horiz = "─" * box_width
    top = f"┌{ '─' * box_width }┐"
    title_line = f"│{title.center(box_width)}│"
    sep = f"├{ '─' * box_width }┤"
    bottom = f"└{ '─' * box_width }┘"

    out = [top, title_line, sep]
    for ln in lines:
        out.append(f"│{ln.ljust(box_width)}│")
    out.append(bottom)

    # Add top categories block after the box
    out.append("")
    out.append("Top Spending Categories:")
    for idx, item in enumerate(top_categories, start=1):
        # item: dict with category, amount, percent
        out.append(f"{idx}. {item['category']:<20} ${item['amount']:>8,.2f}   ({item['percent']:>4.1f}%)")

    return out

def _run_initial_setup_menu():
    user_persistence = UserAccountPersistence()

    while True:
        clear_screen()
        accounts = user_persistence.get_all_accounts()

        if not accounts:
            add_message("--- Welcome to Personal Finance Manager ---")
            add_message("No users registered. Please register to begin.")
            add_message("1. Register New User")
            add_message("Q. Exit")
            display_messages() # Display messages before getting input
            choice = get_user_input("Enter your choice: ").strip().upper()

            if choice == '1':
                if register():
                    # Registration successful, now prompt for login
                    pass # Continue the loop to prompt for login
                else:
                    # Registration failed, continue the loop
                    pass # Continue the loop to prompt for login/register
            elif choice == 'Q':
                break
            else:
                add_message("Invalid choice. Please try again.")

        else:
            add_message("--- Welcome to Personal Finance Manager --- ")
            add_message("1. Login")
            add_message("2. Register")
            add_message("Q. Exit")
            display_messages() # Display messages before getting input
            choice = get_user_input("Enter your choice: ").strip().upper()

            if choice == '1':
                if login(): # Call the standalone login function
                    # Login successful
                    break
                else:
                    # Login failed, continue the loop
                    continue
            elif choice == '2':
                register() # Call the standalone register function
                # After registration, attempt to log in the new user
                # For simplicity, we'll break and let the main loop re-prompt for login
                add_message("Registration successful. Please log in.")
                continue
            elif choice == 'Q':
                break
            else:
                add_message("Invalid choice. Please try again.")

    if SessionManager.is_logged_in():
        current_user = SessionManager.get_current_user()
        if current_user: # Ensure current_user is not None before accessing its attributes
            add_message(f"Welcome, {current_user.username}!")

            # Dashboard will be rendered by the main menu when it first displays
        start()
    else:
        add_message("Exiting Personal Finance Manager.")


if __name__ == '__main__':
    _run_initial_setup_menu()
