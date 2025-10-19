import click
import curses
from src.services.menu_manager import MenuManager
from src.utils.curses_utils import init_curses, teardown_curses, display_message, get_user_input
from src.utils.input_validator import validate_integer

@click.group()
def menu():
    """Manages the hierarchical CLI menu system."""
    pass

@menu.command()
def start():
    """Starts the main hierarchical menu."""
    manager = MenuManager()
    stdscr = None
    try:
        stdscr = init_curses()
        current_menu_id = "main"
        while True:
            stdscr.clear()
            menu_items = manager.get_menu_items(current_menu_id)
            if not menu_items:
                display_message(stdscr, "No menu items found.", 0, 0)
                stdscr.getch()
                break

            manager.display_menu(stdscr, current_menu_id)

            choice = get_user_input(stdscr, "", len(menu_items) + 3, len("Enter your choice: ")).strip().upper()

            if choice == 'Q':
                break
            elif choice == 'B' and current_menu_id != "main":
                current_menu_id = manager.return_to_parent_menu(current_menu_id)
            elif choice == 'H': # Added for help command
                manager.display_help(stdscr, current_menu_id)
                stdscr.getch()
            else:
                is_valid, validated_choice = validate_integer(choice, min_val=1, max_val=len(menu_items))
                if is_valid:
                    selected_item = menu_items[validated_choice - 1]
                    if selected_item.action.startswith("menu:"):
                        current_menu_id = manager.navigate_to_submenu(current_menu_id, selected_item.action.split(":")[1])
                    elif selected_item.action.startswith("command:"):
                        manager.execute_command_action(stdscr, selected_item.action)
                    else:
                        display_message(stdscr, f"Unknown action type: {selected_item.action}", len(menu_items) + 4, 0)
                        stdscr.getch()
                else:
                    display_message(stdscr, f"Invalid input: {validated_choice}. Please enter a number, 'Q', 'B', or 'H'.", len(menu_items) + 4, 0)
                    stdscr.getch()

    except Exception as e:
        if stdscr:
            teardown_curses(stdscr)
        click.echo(f"An error occurred: {e}")
    finally:
        if stdscr:
            teardown_curses(stdscr)

@menu.command()
@click.argument('option_id')
def select(option_id):
    """Selects an option in the current menu (for direct navigation/testing)."""
    click.echo(f"Selecting option: {option_id}")
    # This command would typically be used internally or for testing
    # The main interactive menu handles selection via the 'start' command.

@menu.command()
@click.argument('menu_path')
def navigate(menu_path):
    """Directly navigates to a menu path (for direct navigation/testing)."""
    click.echo(f"Navigating to menu path: {menu_path}")
    # This command would typically be used internally or for testing
    # The main interactive menu handles navigation via the 'start' command.

@menu.command()
def help():
    """Displays contextual help for the current menu."""
    click.echo("Help functionality is integrated into the interactive menu (press 'H').")