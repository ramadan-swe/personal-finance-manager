# src/services/menu_manager.py
from datetime import date
from src.models.menu_item import MenuItem, MenuItemPersistence
from src.models.menu_state import MenuState, MenuStatePersistence
from src.utils.prompt_toolkit_utils import display_menu, get_user_input
from src.utils.input_validator import validate_number, validate_iso_date, validate_type, validate_description, validate_category
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import CategoryManager
from src.services.session_manager import SessionManager

class MenuManager:
    def __init__(self):
        self.menu_item_persistence = MenuItemPersistence()
        self.menu_state_persistence = MenuStatePersistence()
        self.transaction_manager = TransactionManager()

        # Initialize some default menu items if none exist
        if not self.menu_item_persistence.get_all_menu_items():
            self._initialize_default_menu()

    def _initialize_default_menu(self):
        # Main Menu
        self.menu_item_persistence.create_menu_item(MenuItem("main", "Main Menu", "", "Top level menu"))
        self.menu_item_persistence.create_menu_item(MenuItem("view_transactions", "View Transactions", "command:view_transactions", "View all recorded transactions", parent_id="main"))
        self.menu_item_persistence.create_menu_item(MenuItem("add_transaction", "Add Transaction", "command:add_transaction", "Add a new financial transaction", parent_id="main"))
        self.menu_item_persistence.create_menu_item(MenuItem("reports_menu", "Reports", "menu:reports", "Access financial reports", parent_id="main"))
        self.menu_item_persistence.create_menu_item(MenuItem("settings_menu", "Settings", "menu:settings", "Configure application settings", parent_id="main"))

        # Reports Sub-menu
        self.menu_item_persistence.create_menu_item(MenuItem("reports", "Reports Menu", "", "Financial reports", parent_id="reports_menu"))
        self.menu_item_persistence.create_menu_item(MenuItem("monthly_report", "Monthly Report", "command:monthly_report", "Generate monthly financial report", parent_id="reports_menu"))
        self.menu_item_persistence.create_menu_item(MenuItem("category_breakdown", "Category Breakdown", "command:category_breakdown", "View spending by category", parent_id="reports_menu"))

        # Settings Sub-menu
        self.menu_item_persistence.create_menu_item(MenuItem("settings", "Settings Menu", "", "Application settings", parent_id="settings_menu"))
        self.menu_item_persistence.create_menu_item(MenuItem("change_pin", "Change PIN", "command:change_pin", "Change user PIN", parent_id="settings_menu"))

    def get_menu_items(self, parent_id=None):
        all_items = self.menu_item_persistence.get_all_menu_items()
        if parent_id == "main": # Special case for primary menu
            return [item for item in all_items if item.parent_id == "main"]
        return [item for item in all_items if item.parent_id == parent_id]

    def get_primary_menu(self):
        return self.get_menu_items(parent_id="main")



    def navigate_to_submenu(self, current_menu_id, target_menu_id, user_id="default_user"):
        # For simplicity, assuming a single user for now
        menu_state = self.menu_state_persistence.get_menu_state(user_id)
        if not menu_state:
            menu_state = MenuState(user_id=user_id, navigation_stack=[current_menu_id])
            self.menu_state_persistence.create_menu_state(menu_state)
        else:
            menu_state.navigation_stack.append(current_menu_id)
            self.menu_state_persistence.update_menu_state(menu_state)
        return target_menu_id

    def return_to_parent_menu(self, current_menu_id, user_id="default_user"):
        menu_state = self.menu_state_persistence.get_menu_state(user_id)
        if menu_state and menu_state.navigation_stack:
            parent_menu_id = menu_state.navigation_stack.pop()
            self.menu_state_persistence.update_menu_state(menu_state)
            return parent_menu_id
        return "main" # Fallback to main menu

    def get_contextual_help(self, menu_id, item_id=None):
        if item_id:
            menu_item = self.menu_item_persistence.get_menu_item(item_id)
            return menu_item.help_text if menu_item else "No help available for this item."
        else:
            # Return help for the current menu
            menu_items = self.get_menu_items(menu_id)
            help_text = f"--- Help for {menu_id.replace('_', ' ').title()} Menu ---\n"
            for item in menu_items:
                help_text += f"- {item.label}: {item.help_text}\n"
            help_text += "\nQ: Exit, B: Back, H: Help"
            return help_text

    def execute_command_action(self, action_string):
        command_name = action_string.split(":")[1]
        user_id = SessionManager.get_current_user().username
        if command_name == "add_transaction":
            self._handle_add_transaction(user_id)
        elif command_name == "view_transactions":
            self._handle_view_transactions(user_id)
        elif command_name == "monthly_report":
            self._handle_monthly_report()
        elif command_name == "category_breakdown":
            self._handle_category_breakdown()
        elif command_name == "change_pin":
            self._handle_change_pin()
        else:
            print(f"Unknown command: {command_name}")

    def _handle_add_transaction(self, user_id):
        print("--- Add New Transaction ---")
        
        while True:
            amount_str = get_user_input("Amount: ")
            is_valid, amount = validate_number(amount_str)
            if is_valid:
                break
            print(f"Error: {amount}")

        while True:
            date_str = get_user_input(f"Date (YYYY-MM-DD) [default: {date.today().isoformat()}]: ")
            if not date_str:
                transaction_date = date.today().isoformat()
                break
            is_valid, transaction_date = validate_iso_date(date_str)
            if is_valid:
                break
            print(f"Error: {transaction_date}")
        
        while True:
            type_str = get_user_input("Type (income/expense): ")
            is_valid, transaction_type = validate_type(type_str)
            if is_valid:
                break
            print(f"Error: {transaction_type}")

        while True:
            description = get_user_input("Description: ")
            is_valid, description = validate_description(description)
            if is_valid:
                break
            print(f"Error: {description}")

        while True:
            categories = CategoryManager.get_categories()
            print(f"Available Categories: {', '.join(categories)}")
            category = get_user_input("Category: ")
            is_valid, category_error = validate_category(category)
            if not is_valid:
                print(f"Error: {category_error}")
                continue
            if not CategoryManager.is_valid_category(category):
                print(f"Error: Invalid category '{category}'")
                continue
            break

        if self.transaction_manager.add_transaction(amount, transaction_date, transaction_type, description, category, user_id):
            print("Transaction added successfully.")
        else:
            print("Failed to add transaction.")
        get_user_input("Press Enter to continue...")

    def _handle_view_transactions(self, user_id):
        print("--- View Transactions ---")
        transactions = self.transaction_manager.get_all_transactions(user_id)
        if not transactions:
            print("No transactions found.")
        else:
            for t in transactions:
                print(f"ID: {t.id[:8]}..., Amount: {t.amount}, Date: {t.date}, Type: {t.type}, Desc: {t.description}, Cat: {t.category}")
        get_user_input("Press Enter to continue...")

    def _handle_monthly_report(self):
        print("Monthly report functionality not yet implemented.")
        get_user_input("Press Enter to continue...")

    def _handle_category_breakdown(self):
        print("Category breakdown functionality not yet implemented.")
        get_user_input("Press Enter to continue...")

    def _handle_change_pin(self):
        print("Change PIN functionality not yet implemented.")
        get_user_input("Press Enter to continue...")
