from src.cli.menu import start
from src.cli.user import register, login
from src.models.user_account import UserAccountPersistence
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input
from src.services.data_persistence import DataPersistenceService
from src.services.transaction_manager import TransactionManager

from src.utils.prompt_toolkit_utils import get_user_input, clear_screen, add_message, display_messages
from src.services.reporting import generate_dashboard_summary, generate_monthly_report
from src.services.transaction_manager import TransactionManager

def _run_initial_setup_menu():
    user_persistence = UserAccountPersistence()
    data_persistence_service = DataPersistenceService()
    transaction_manager = TransactionManager(data_persistence_service)

    while True:
        clear_screen()
        accounts = user_persistence.get_all_accounts()

        if not accounts:
            add_message("""
--- Welcome to Personal Finance Manager ---
No users registered. Please register to begin.
1. Register New User
Q. Exit""")
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
            add_message("""
--- Welcome to Personal Finance Manager ---
1. Login
2. Register
Q. Exit""")
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
        start(transaction_manager) # Pass the shared transaction_manager
    else:
        add_message("Exiting Personal Finance Manager.")


if __name__ == '__main__':
    _run_initial_setup_menu()
