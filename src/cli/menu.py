import click
from src.services.menu_manager import MenuManager
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input, display_menu
from src.utils.input_validator import validate_integer

@click.group()
def menu():
    """Manages the hierarchical CLI menu system."""
    pass

@menu.command()
def start():
    """Starts the main hierarchical menu."""
    manager = MenuManager()
    current_menu_id = "main"
    user_id = SessionManager.get_current_user().username
    while True:
        menu_items = manager.get_menu_items(current_menu_id)
        if not menu_items:
            print("No menu items found.")
            break
        
        # Display the menu using the utility function, not a method of MenuManager
        # The title should reflect the current menu, and items should be passed directly
        menu_title = next((item.label for item in manager.menu_item_persistence.get_all_menu_items() if item.id == current_menu_id), "Menu") # This line is causing the error
        display_menu(menu_title, menu_items)

        choice = get_user_input("Enter your choice: ").strip().upper()

        if choice == 'Q':
            break
        elif choice == 'B' and current_menu_id != "main":
            current_menu_id = manager.return_to_parent_menu(current_menu_id, user_id)
        elif choice == 'H': # Added for help command
            print(manager.get_contextual_help(current_menu_id))
        else:
            is_valid, validated_choice = validate_integer(choice, min_val=1, max_val=len(menu_items))
            if is_valid:
                selected_item = menu_items[validated_choice - 1]
                if selected_item.action.startswith("menu:"):
                    current_menu_id = manager.navigate_to_submenu(current_menu_id, selected_item.action.split(":")[1], user_id)
                elif selected_item.action.startswith("command:"):
                    manager.execute_command_action(selected_item.action)
                else:
                    print(f"Unknown action type: {selected_item.action}")
            else:
                print(f"Invalid input: {validated_choice}. Please enter a number, 'Q', 'B', or 'H'.")

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