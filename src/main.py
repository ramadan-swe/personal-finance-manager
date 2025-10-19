from src.cli.menu import start
from src.cli.user import register, login # Import register and login functions
from src.models.user_account import UserAccountPersistence
from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input
from src.utils.input_validator import validate_pin, validate_username

from src.utils.prompt_toolkit_utils import get_user_input, clear_screen

def _run_initial_setup_menu():
    user_persistence = UserAccountPersistence()

    while True:
        clear_screen()
        accounts = user_persistence.get_all_accounts()

        if not accounts:
            print("--- Welcome to Personal Finance Manager ---")
            print("No users registered. Please register to begin.")
            print("1. Register New User")
            print("Q. Exit")
            choice = get_user_input("Enter your choice: ").strip().upper()

            if choice == '1':
                if register(): # Call the standalone register function
                    # Registration successful, now prompt for login
                    pass # Continue the loop to prompt for login
                else:
                    # Registration failed, continue the loop
                    pass # Continue the loop to prompt for login/register
            elif choice == 'Q':
                break
            else:
                print("Invalid choice. Please try again.")

        else:
            print("--- Welcome to Personal Finance Manager --- ")
            print("1. Login")
            print("2. Register")
            print("Q. Exit")
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
                print("Registration successful. Please log in.")
                continue
            elif choice == 'Q':
                break
            else:
                print("Invalid choice. Please try again.")

    if SessionManager.is_logged_in():
        current_user = SessionManager.get_current_user()
        if current_user: # Ensure current_user is not None before accessing its attributes
            print(f"Welcome, {current_user.username}!")
        start()
    else:
        print("Exiting Personal Finance Manager.")


if __name__ == '__main__':
    _run_initial_setup_menu()
