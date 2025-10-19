# src/services/menu_manager.py
from src.models.menu_item import MenuItem, MenuItemPersistence
from src.models.menu_state import MenuState, MenuStatePersistence
from src.utils.curses_utils import display_message, get_user_input
from src.utils.input_validator import validate_number, validate_iso_date, validate_type, validate_description, validate_category
from src.services.transaction_manager import TransactionManager
from src.services.category_manager import CategoryManager

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

    def display_menu(self, stdscr, menu_id, current_user_id=None):
        stdscr.clear()
        menu_items = self.get_menu_items(menu_id)
        if not menu_items:
            display_message(stdscr, "No menu items found.", 0, 0)
            return

        # Placeholder for handling long menus (pagination/search) - FR-005
        # For now, assumes all menu items fit on screen given Max items per menu: 20 constraint.
        # Future enhancement: implement pagination or search if menu_items exceeds screen height.

        # Display menu title (assuming menu_id is also the title for now)
        display_message(stdscr, f"--- {menu_id.replace('_', ' ').title()} Menu ---", 0, 0)
        for i, item in enumerate(menu_items):
            display_message(stdscr, f"{i+1}. {item.label}", i+1, 0)
        display_message(stdscr, "Q. Exit", len(menu_items) + 1, 0)
        if menu_id != "main":
            display_message(stdscr, "B. Back", len(menu_items) + 2, 0)
        display_message(stdscr, "Enter your choice: ", len(menu_items) + 3, 0)

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

    def display_help(self, stdscr, menu_id, item_id=None):
        help_content = self.get_contextual_help(menu_id, item_id)
        stdscr.clear()
        display_message(stdscr, help_content, 0, 0)
        display_message(stdscr, "Press any key to return...", help_content.count('\n') + 2, 0)

    def execute_command_action(self, stdscr, action_string):
        command_name = action_string.split(":")[1]
        if command_name == "add_transaction":
            self._handle_add_transaction(stdscr)
        elif command_name == "view_transactions":
            self._handle_view_transactions(stdscr)
        elif command_name == "monthly_report":
            self._handle_monthly_report(stdscr)
        elif command_name == "category_breakdown":
            self._handle_category_breakdown(stdscr)
        elif command_name == "change_pin":
            self._handle_change_pin(stdscr)
        else:
            display_message(stdscr, f"Unknown command: {command_name}", 0, 0)
            stdscr.getch()

    def _handle_add_transaction(self, stdscr):
        stdscr.clear()
        display_message(stdscr, "--- Add New Transaction ---", 0, 0)
        
        amount_str = get_user_input(stdscr, "Amount: ", 2, 0)
        is_valid, amount = validate_number(amount_str)
        if not is_valid:
            display_message(stdscr, f"Error: {amount}. Press any key to continue.", 4, 0)
            stdscr.getch()
            return

        date_str = get_user_input(stdscr, "Date (YYYY-MM-DD): ", 3, 0)
        is_valid, date = validate_iso_date(date_str)
        if not is_valid:
            display_message(stdscr, f"Error: {date}. Press any key to continue.", 4, 0)
            stdscr.getch()
            return

        type_str = get_user_input(stdscr, "Type (income/expense): ", 4, 0)
        is_valid, transaction_type = validate_type(type_str)
        if not is_valid:
            display_message(stdscr, f"Error: {transaction_type}. Press any key to continue.", 6, 0)
            stdscr.getch()
            return

        description = get_user_input(stdscr, "Description: ", 5, 0)
        is_valid, description = validate_description(description)
        if not is_valid:
            display_message(stdscr, f"Error: {description}. Press any key to continue.", 7, 0)
            stdscr.getch()
            return

        categories = CategoryManager.get_categories()
        display_message(stdscr, f"Available Categories: {', '.join(categories)}", 7, 0)
        category = get_user_input(stdscr, "Category: ", 8, 0)
        is_valid, category = validate_category(category)
        if not is_valid:
            display_message(stdscr, f"Error: {category}. Press any key to continue.", 10, 0)
            stdscr.getch()
            return
        if not CategoryManager.is_valid_category(category):
            display_message(stdscr, f"Error: Invalid category '{category}'. Press any key to continue.", 10, 0)
            stdscr.getch()
            return

        if self.transaction_manager.add_transaction(amount, date, transaction_type, description, category):
            display_message(stdscr, "Transaction added successfully. Press any key to continue.", 10, 0)
        else:
            display_message(stdscr, "Failed to add transaction. Press any key to continue.", 10, 0)
        stdscr.getch()

    def _handle_view_transactions(self, stdscr):
        stdscr.clear()
        display_message(stdscr, "--- View Transactions ---", 0, 0)
        transactions = self.transaction_manager.get_all_transactions()
        if not transactions:
            display_message(stdscr, "No transactions found.", 2, 0)
        else:
            y_offset = 2
            for i, t in enumerate(transactions):
                display_message(stdscr, f"ID: {t.id[:8]}..., Amount: {t.amount}, Date: {t.date}, Type: {t.type}, Desc: {t.description}, Cat: {t.category}", y_offset + i, 0)
        display_message(stdscr, "Press any key to continue...", y_offset + len(transactions) + 1, 0)
        stdscr.getch()

    def _handle_monthly_report(self, stdscr):
        display_message(stdscr, "Monthly report functionality not yet implemented.", 0, 0)
        stdscr.getch()

    def _handle_category_breakdown(self, stdscr):
        display_message(stdscr, "Category breakdown functionality not yet implemented.", 0, 0)
        stdscr.getch()

    def _handle_change_pin(self, stdscr):
        display_message(stdscr, "Change PIN functionality not yet implemented.", 0, 0)
        stdscr.getch()