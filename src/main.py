import click
from src.cli.user import user
from src.cli.transaction import transaction
from src.cli.menu import menu, start as menu_start_command # Import start command specifically
from src.models.user_account import UserAccountPersistence
from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input
from src.utils.input_validator import validate_pin, validate_username

@click.group()
def finance():
    """A personal finance management CLI tool."""
    pass

finance.add_command(user)
finance.add_command(transaction)
finance.add_command(menu)

@finance.command(hidden=True) # Hide this from default help
def _initial_setup_menu_command():
    _run_initial_setup_menu()

from src.utils.prompt_toolkit_utils import get_user_input, clear_screen

# ... (rest of the file is the same until _run_initial_setup_menu)

def _run_initial_setup_menu():
    user_persistence = UserAccountPersistence()
    user_service = UserManagementService()

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
                username = get_user_input("Enter desired username: ")
                pin = get_user_input("Enter PIN: ", hide_input=True)
                pin_confirm = get_user_input("Confirm PIN: ", hide_input=True)

                if pin != pin_confirm:
                    print("PINs do not match. Please try again.")
                    continue
                
                is_valid_pin, pin_msg = validate_pin(pin)
                if not is_valid_pin:
                    print(f"Invalid PIN: {pin_msg}. Please try again.")
                    continue

                if user_service.register_user(username, pin):
                    print(f"User '{username}' registered successfully. Please log in.")
                    break
                else:
                    print(f"Error: User '{username}' already exists or registration failed. Please try again.")
                    continue
            elif choice == 'Q':
                break
            else:
                print("Invalid choice. Please try again.")

        else:
            print("--- Welcome Back --- ")
            print("1. Login")
            print("2. Register")
            print("Q. Exit")
            choice = get_user_input("Enter your choice: ").strip().upper()

            if choice == '1':
                username = get_user_input("Enter username: ")
                pin = get_user_input("Enter PIN: ", hide_input=True)

                user_account = user_service.authenticate_user(username, pin)
                if user_account:
                    SessionManager.login_user(user_account)
                    print(f"Logged in as '{username}'.")
                    break
                else:
                    print("Invalid username or PIN. Please try again.")
                    continue
            elif choice == '2':
                username = get_user_input("Enter desired username: ")
                pin = get_user_input("Enter PIN: ", hide_input=True)
                pin_confirm = get_user_input("Confirm PIN: ", hide_input=True)

                if pin != pin_confirm:
                    print("PINs do not match. Please try again.")
                    continue
                
                is_valid_pin, pin_msg = validate_pin(pin)
                if not is_valid_pin:
                    print(f"Invalid PIN: {pin_msg}. Please try again.")
                    continue

                if user_service.register_user(username, pin):
                    print(f"User '{username}' registered successfully. Please log in.")
                else:
                    print(f"Error: User '{username}' already exists or registration failed. Please try again.")
                    continue
            elif choice == 'Q':
                break
            else:
                print("Invalid choice. Please try again.")

    if SessionManager.is_logged_in():
        click.echo(f"Welcome, {SessionManager.get_current_user().username}!")
        menu_start_command.callback() # Call the callback function of the start command
    else:
        click.echo("Exiting Personal Finance Manager.")


if __name__ == '__main__':
    # This is a workaround to make _initial_setup_menu the default command
    # if no other command is specified.
    # A more robust solution for complex CLIs might involve a custom Click Group class.
    # For now, if no subcommand is given, we'll call _run_initial_setup_menu.
    import sys
    if len(sys.argv) == 1:
        _run_initial_setup_menu()
    else:
        finance()
