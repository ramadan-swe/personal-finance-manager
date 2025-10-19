import click
import curses
from src.cli.user import user
from src.cli.transaction import transaction
from src.cli.menu import menu, start as menu_start_command # Import start command specifically
from src.models.user_account import UserAccountPersistence
from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
from src.utils.curses_utils import init_curses, teardown_curses, display_message, get_user_input
from src.utils.input_validator import validate_pin

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

def _run_initial_setup_menu():
    user_persistence = UserAccountPersistence()
    user_service = UserManagementService()
    stdscr = None

    try:
        stdscr = init_curses()
        while True:
            stdscr.clear()
            accounts = user_persistence.get_all_accounts()

            if not accounts:
                display_message(stdscr, "--- Welcome to Personal Finance Manager ---", 0, 0)
                display_message(stdscr, "No users registered. Please register to begin.", 2, 0)
                display_message(stdscr, "1. Register New User", 4, 0)
                display_message(stdscr, "Q. Exit", 5, 0)
                choice = get_user_input(stdscr, "Enter your choice: ", 7, 0).strip().upper()

                if choice == '1':
                    username = get_user_input(stdscr, "Enter desired username: ", 9, 0)
                    pin = get_user_input(stdscr, "Enter PIN: ", 10, 0, hide_input=True)
                    pin_confirm = get_user_input(stdscr, "Confirm PIN: ", 11, 0, hide_input=True)

                    if pin != pin_confirm:
                        display_message(stdscr, "PINs do not match. Press any key to retry.", 13, 0)
                        stdscr.getch()
                        continue
                    
                    is_valid_pin, pin_msg = validate_pin(pin)
                    if not is_valid_pin:
                        display_message(stdscr, f"Invalid PIN: {pin_msg}. Press any key to retry.", 13, 0)
                        stdscr.getch()
                        continue

                    if user_service.register_user(username, pin):
                        display_message(stdscr, f"User '{username}' registered successfully. Press any key to log in.", 13, 0)
                        stdscr.getch()
                        # After registration, proceed to login flow
                        break 
                    else:
                        display_message(stdscr, f"Error: User '{username}' already exists or registration failed. Press any key to retry.", 13, 0)
                        stdscr.getch()
                        continue
                elif choice == 'Q':
                    break
                else:
                    display_message(stdscr, "Invalid choice. Press any key to retry.", 9, 0)
                    stdscr.getch()

            else:
                display_message(stdscr, "--- Welcome Back --- ", 0, 0)
                display_message(stdscr, "1. Login", 2, 0)
                display_message(stdscr, "Q. Exit", 3, 0)
                choice = get_user_input(stdscr, "Enter your choice: ", 5, 0).strip().upper()

                if choice == '1':
                    username = get_user_input(stdscr, "Enter username: ", 7, 0)
                    pin = get_user_input(stdscr, "Enter PIN: ", 8, 0, hide_input=True)

                    user_account = user_service.authenticate_user(username, pin)
                    if user_account:
                        SessionManager.login_user(user_account)
                        display_message(stdscr, f"Logged in as '{username}'. Press any key to continue to main menu.", 10, 0)
                        stdscr.getch()
                        break # Exit initial menu loop to main app
                    else:
                        display_message(stdscr, "Invalid username or PIN. Press any key to retry.", 10, 0)
                        stdscr.getch()
                        continue
                elif choice == 'Q':
                    break
                else:
                    display_message(stdscr, "Invalid choice. Press any key to retry.", 7, 0)
                    stdscr.getch()

    except Exception as e:
        if stdscr:
            teardown_curses(stdscr)
        click.echo(f"An error occurred: {e}")
    finally:
        if stdscr:
            teardown_curses(stdscr)

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
