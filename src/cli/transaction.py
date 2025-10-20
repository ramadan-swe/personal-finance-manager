from datetime import datetime
from src.services.transaction_manager import TransactionManager
from src.models.transaction import Currencies, PaymentMethod
from src.utils.validators import validate_amount, validate_date, validate_type, validate_description, validate_category, validate_payment_method, validate_currency
from src.services.category_manager import get_categories, is_valid_category
from src.utils.prompt_toolkit_utils import get_user_input, add_message, CANCEL_COMMAND
from src.services.session_manager import SessionManager
from src.services.data_persistence import DataPersistenceService

def _get_validated_input(prompt, default_value=None, validator_func=None, allow_empty=False, allow_skip=False, is_edit_mode=False, display_current_or_default=True, error_message="Invalid input."):
    while True:
        prompt_suffix = ""
        if display_current_or_default:
            if is_edit_mode:
                prompt_suffix = f' (current: {default_value}, type \'cancel\' to return to main menu, leave blank to keep current)'
            else:
                prompt_suffix = f' (default: {default_value}, type \'cancel\' to return to main menu)'
        else:
            prompt_suffix = ' (type \'cancel\' to return to main menu)'

        input_str = get_user_input(f'{prompt}{prompt_suffix}: ')
        if input_str.lower() == CANCEL_COMMAND:
            return CANCEL_COMMAND
        
        if not input_str and allow_skip:
            return None # Indicates that the user wants to keep the current value

        if not input_str and not allow_empty and default_value is not None:
            input_str = default_value

        if validator_func and input_str is not None:
            is_valid, validated_value = validator_func(input_str)
            if not is_valid:
                add_message(f"Error: {validated_value}")
            else:
                return validated_value
        elif input_str is not None:
            return input_str
        else:
            add_message(error_message)


def add_transaction_command(manager: TransactionManager):
    """Adds a new financial transaction."""
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in. Please log in to add transactions.")
        return
    user_id = current_user.username

    amount = None
    while amount is None:
        amount_input = _get_validated_input('Amount of the transaction', validator_func=validate_amount, display_current_or_default=False)
        if amount_input == CANCEL_COMMAND:
            add_message("Transaction addition cancelled.")
            return
        if amount_input is not None:
            amount = amount_input

    default_date = datetime.now().strftime('%Y-%m-%d')
    date_str = _get_validated_input(f'Date of the transaction (YYYY-MM-DD)', default_date, validate_date, is_edit_mode=False, display_current_or_default=True)
    if date_str == CANCEL_COMMAND:
        add_message("Transaction addition cancelled.")
        return

    default_type = 'expense'
    type_str = _get_validated_input('Type of the transaction (income/expense)', default_type, validate_type, is_edit_mode=False, display_current_or_default=True)
    if type_str == CANCEL_COMMAND:
        add_message("Transaction addition cancelled.")
        return

    description = _get_validated_input('Description of the transaction', '', validate_description, allow_empty=True, is_edit_mode=False, display_current_or_default=False)
    if description == CANCEL_COMMAND:
        add_message("Transaction addition cancelled.")
        return

    default_category = 'Uncategorized'
    category = None
    while category is None:
        category_input = _get_validated_input('Category of the transaction', default_category, validate_category, is_edit_mode=False, display_current_or_default=True)
        if category_input == CANCEL_COMMAND:
            add_message("Transaction addition cancelled.")
            return
        if not is_valid_category(category_input):
            add_message(f"Error: Invalid category '{category_input}'. Use 'finance category list' to see available categories.")
        else:
            category = category_input

    default_payment_method = 'debit'
    payment_method_str = _get_validated_input('Payment method (debit, credit, cash)', default_payment_method, validate_payment_method, is_edit_mode=False, display_current_or_default=True)
    if payment_method_str == CANCEL_COMMAND:
        add_message("Transaction addition cancelled.")
        return

    default_currency = 'USD'
    currency_str = _get_validated_input('Currency (e.g., USD, EUR, EGP)', default_currency, validate_currency, is_edit_mode=False, display_current_or_default=True)
    if currency_str == CANCEL_COMMAND:
        add_message("Transaction addition cancelled.")
        return

    if manager.add_transaction(amount, date_str, type_str, description, category, user_id, payment_method_str, currency_str):
        add_message("Transaction added successfully.")
    else:
        add_message("Error: Failed to add transaction.")

def edit_transaction_command(transaction_id=None, manager=None):
    """Edits an existing financial transaction."""
    if manager is None:
        add_message("Error: TransactionManager not provided to edit_transaction_command.")
        return

    if transaction_id is None:
        transaction_id = get_user_input('ID of the transaction to edit: ')
    
    existing_transaction = manager.get_transaction(transaction_id)

    if not existing_transaction:
        add_message(f"Error: Transaction with ID '{transaction_id}' not found.")
        return

    updates = {}

    # Refactor edit_transaction_command to use _get_validated_input
    amount = _get_validated_input(f'New amount', existing_transaction.amount, validate_amount, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if amount == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if amount is not None:
        updates['amount'] = amount

    date_str = _get_validated_input(f'New date (YYYY-MM-DD)', existing_transaction.date, validate_date, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if date_str == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if date_str is not None:
        updates['date'] = date_str

    type_str = _get_validated_input(f'New type (income/expense)', existing_transaction.type, validate_type, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if type_str == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if type_str is not None:
        updates['type'] = type_str

    description = _get_validated_input(f'New description', existing_transaction.description, validate_description, allow_empty=True, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if description == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if description is not None:
        updates['description'] = description

    category = _get_validated_input(f'New category', existing_transaction.category, validate_category, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if category == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if category is not None:
        if not is_valid_category(category):
            add_message(f"Error: Invalid category '{category}'. Use 'finance category list' to see available categories.")
            return
        updates['category'] = category

    payment_method_str = _get_validated_input(f'New payment method (debit, credit, cash)', existing_transaction.payment_method.value, validate_payment_method, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if payment_method_str == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if payment_method_str is not None:
        updates['payment_method'] = payment_method_str

    currency_str = _get_validated_input(f'New currency (e.g., USD, EUR, EGP)', existing_transaction.currency.short_name, validate_currency, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if currency_str == CANCEL_COMMAND:
        add_message("Transaction edit cancelled.")
        return
    if currency_str is not None:
        updates['currency'] = currency_str

    if not updates:
        add_message("No updates provided.")
        return

    if manager.update_transaction(transaction_id, **updates):
        add_message(f"Transaction '{transaction_id}' updated successfully.")
    else:
        add_message(f"Error: Failed to update transaction '{transaction_id}'.")

def delete_transaction_command(transaction_id=None, manager=None):
    """Deletes an existing financial transaction."""
    if manager is None:
        add_message("Error: TransactionManager not provided to delete_transaction_command.")
        return

    if transaction_id is None:
        transaction_id = get_user_input('ID of the transaction to delete: ')
    
    confirm = get_user_input(f"Are you sure you want to delete transaction '{transaction_id}'? This action cannot be undone. (yes/no): ").lower()
    if confirm != 'yes':
        add_message("Deletion cancelled.")
        return

    if manager.delete_transaction(transaction_id):
        add_message(f"Transaction '{transaction_id}' deleted successfully.")
    else:
        add_message(f"Error: Transaction '{transaction_id}' not found or failed to delete.")
