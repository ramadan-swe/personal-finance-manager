from src.services.menu_manager import get_menu_items, get_menu_title, navigate_to_submenu, return_to_parent_menu, get_contextual_help, execute_command_action, initialize_default_menu
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input, display_menu
from src.utils.input_validator import validate_integer

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