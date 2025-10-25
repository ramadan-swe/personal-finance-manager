from src.cli.menu import start
from src.cli.user import register, login
from src.models.user_account import UserAccountPersistence
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input, clear_screen, add_message, display_messages
from src.services.data_persistence import DataPersistenceService
from src.services.transaction_manager import TransactionManager

def _handle_no_accounts():
    """
    Handles the menu when no user accounts exist.
    Prompts for registration or exit.
    """
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
        return 'exit'
    else:
        add_message("Invalid choice. Please try again.")
    return 'continue'

def _handle_existing_accounts():
    """
    Handles the menu when user accounts exist.
    Prompts for login, registration, or exit.
    """
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
            return 'login_success'
        else:
            # Login failed, continue the loop
            return 'continue'
    elif choice == '2':
        register() # Call the standalone register function
        # After registration, attempt to log in the new user
        # For simplicity, we'll break and let the main loop re-prompt for login
        add_message("Registration successful. Please log in.")
        return 'continue'
    elif choice == 'Q':
        return 'exit'
    else:
        add_message("Invalid choice. Please try again.")
        return 'continue'

def _start_main_menu(transaction_manager):
    """
    Starts the main application menu if user is logged in.
    """
    current_user = SessionManager.get_current_user()
    if current_user: # Ensure current_user is not None before accessing its attributes
        add_message(f"Welcome, {current_user.username}!")
    start(transaction_manager) # Pass the shared transaction_manager

def _run_initial_setup_menu():
    """
    Runs the initial setup menu for user registration and login.

    Handles the main entry point logic for the application, prompting users to register or login,
    and starting the main menu if login is successful.
    """
    user_persistence = UserAccountPersistence()
    data_persistence_service = DataPersistenceService()
    transaction_manager = TransactionManager(data_persistence_service)

    while True:
        clear_screen()
        accounts = user_persistence.get_all_accounts()

        if not accounts:
            result = _handle_no_accounts()
            if result == 'exit':
                break
        else:
            result = _handle_existing_accounts()
            if result == 'login_success':
                break
            elif result == 'exit':
                break

    if SessionManager.is_logged_in():
        _start_main_menu(transaction_manager)
    else:
        add_message("Exiting Personal Finance Manager.")


if __name__ == '__main__':
    _run_initial_setup_menu()
