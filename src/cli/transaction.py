from datetime import datetime
from src.services.transaction_manager import TransactionManager

from src.utils.input_validator import _get_validated_input, validate_amount, validate_iso_date as validate_date, validate_type, validate_description, validate_category, validate_payment_method, validate_currency
from src.services.category_manager import is_valid_category
from src.utils.prompt_toolkit_utils import get_user_input, add_message, CANCEL_COMMAND
from src.services.session_manager import SessionManager





def _prompt_transaction_details():
    """
    Prompts user for transaction details and returns a dict or None if cancelled.
    """
    amount = None
    while amount is None:
        amount_input = _get_validated_input('Amount of the transaction', validator_func=validate_amount, display_current_or_default=False)
        if amount_input == CANCEL_COMMAND:
            return None
        if amount_input is not None:
            amount = amount_input

    default_date = datetime.now().strftime('%Y-%m-%d')
    date_str = _get_validated_input(f'Date of the transaction (YYYY-MM-DD)', default_date, validate_date, is_edit_mode=False, display_current_or_default=True)
    if date_str == CANCEL_COMMAND:
        return None

    default_type = 'expense'
    type_str = _get_validated_input('Type of the transaction (income/expense)', default_type, validate_type, is_edit_mode=False, display_current_or_default=True)
    if type_str == CANCEL_COMMAND:
        return None

    description = _get_validated_input('Description of the transaction', '', validate_description, allow_empty=True, is_edit_mode=False, display_current_or_default=False)
    if description == CANCEL_COMMAND:
        return None

    default_category = 'Uncategorized'
    category = None
    while category is None:
        category_input = _get_validated_input('Category of the transaction', default_category, validate_category, is_edit_mode=False, display_current_or_default=True)
        if category_input == CANCEL_COMMAND:
            return None
        if not is_valid_category(category_input):
            add_message(f"Error: Invalid category '{category_input}'. Use 'finance category list' to see available categories.")
        else:
            category = category_input

    default_payment_method = 'debit'
    payment_method_str = _get_validated_input('Payment method (debit, credit, cash)', default_payment_method, validate_payment_method, is_edit_mode=False, display_current_or_default=True)
    if payment_method_str == CANCEL_COMMAND:
        return None

    default_currency = 'USD'
    currency_str = _get_validated_input('Currency (e.g., USD, EUR, EGP)', default_currency, validate_currency, is_edit_mode=False, display_current_or_default=True)
    if currency_str == CANCEL_COMMAND:
        return None

    return {
        'amount': amount,
        'date': date_str,
        'type': type_str,
        'description': description,
        'category': category,
        'payment_method': payment_method_str,
        'currency': currency_str
    }

def _save_transaction(details, manager, user_id):
    """
    Saves the transaction using the manager.
    """
    if manager.add_transaction(**details, user_id=user_id):
        add_message("Transaction added successfully.")
    else:
        add_message("Error: Failed to add transaction.")

def add_transaction_command(manager: TransactionManager):
    """Adds a new financial transaction."""
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in. Please log in to add transactions.")
        return
    user_id = current_user.username

    details = _prompt_transaction_details()
    if details is None:
        add_message("Transaction addition cancelled.")
        return

    _save_transaction(details, manager, user_id)

def _load_existing_transaction(transaction_id, manager):
    """
    Loads an existing transaction by ID.
    Returns the transaction or None if not found.
    """
    if transaction_id is None:
        transaction_id = get_user_input('ID of the transaction to edit: ')
    
    existing_transaction = manager.get_transaction(transaction_id)
    if not existing_transaction:
        add_message(f"Error: Transaction with ID '{transaction_id}' not found.")
        return None
    return existing_transaction

def _prompt_updates(existing_transaction):
    """
    Prompts for updates to the transaction.
    Returns updates dict or None if cancelled.
    """
    updates = {}

    amount = _get_validated_input(f'New amount', existing_transaction.amount, validate_amount, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if amount == CANCEL_COMMAND:
        return None
    if amount is not None:
        updates['amount'] = amount

    date_str = _get_validated_input(f'New date (YYYY-MM-DD)', existing_transaction.date, validate_date, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if date_str == CANCEL_COMMAND:
        return None
    if date_str is not None:
        updates['date'] = date_str

    type_str = _get_validated_input(f'New type (income/expense)', existing_transaction.type, validate_type, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if type_str == CANCEL_COMMAND:
        return None
    if type_str is not None:
        updates['type'] = type_str

    description = _get_validated_input(f'New description', existing_transaction.description, validate_description, allow_empty=True, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if description == CANCEL_COMMAND:
        return None
    if description is not None:
        updates['description'] = description

    category = _get_validated_input(f'New category', existing_transaction.category, validate_category, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if category == CANCEL_COMMAND:
        return None
    if category is not None:
        if not is_valid_category(category):
            add_message(f"Error: Invalid category '{category}'. Use 'finance category list' to see available categories.")
            return None
        updates['category'] = category

    payment_method_str = _get_validated_input(f'New payment method (debit, credit, cash)', existing_transaction.payment_method.value, validate_payment_method, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if payment_method_str == CANCEL_COMMAND:
        return None
    if payment_method_str is not None:
        updates['payment_method'] = payment_method_str

    currency_str = _get_validated_input(f'New currency (e.g., USD, EUR, EGP)', existing_transaction.currency.short_name, validate_currency, allow_skip=True, is_edit_mode=True, display_current_or_default=True)
    if currency_str == CANCEL_COMMAND:
        return None
    if currency_str is not None:
        updates['currency'] = currency_str

    return updates

def _apply_updates(transaction_id, updates, manager):
    """
    Applies updates to the transaction.
    """
    if not updates:
        add_message("No updates provided.")
        return

    if manager.update_transaction(transaction_id, **updates):
        add_message(f"Transaction '{transaction_id}' updated successfully.")
    else:
        add_message(f"Error: Failed to update transaction '{transaction_id}'.")

def edit_transaction_command(transaction_id=None, manager=None):
    """Edits an existing financial transaction."""
    if manager is None:
        add_message("Error: TransactionManager not provided to edit_transaction_command.")
        return

    existing_transaction = _load_existing_transaction(transaction_id, manager)
    if existing_transaction is None:
        return

    updates = _prompt_updates(existing_transaction)
    if updates is None:
        add_message("Transaction edit cancelled.")
        return

    _apply_updates(existing_transaction.id, updates, manager)

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
