from src.services.transaction_manager import TransactionManager
from src.models.transaction import Transaction
from src.utils.validators import validate_amount, validate_date, validate_type, validate_description, validate_category
from src.services.category_manager import get_categories, is_valid_category # Updated import
from src.utils.prompt_toolkit_utils import get_user_input # Added import

def add():
    """Adds a new financial transaction."""
    amount = get_user_input('Amount of the transaction: ')
    date_str = get_user_input('Date of the transaction (YYYY-MM-DD): ')
    type_str = get_user_input('Type of the transaction (income/expense): ')
    description = get_user_input('Description of the transaction: ')
    category = get_user_input('Category of the transaction: ')

    is_valid, validated_amount = validate_amount(amount)
    if not is_valid:
        print(f"Error: {validated_amount}")
        return

    is_valid, validated_date = validate_date(date_str)
    if not is_valid:
        print(f"Error: {validated_date}")
        return

    is_valid, validated_type = validate_type(type_str)
    if not is_valid:
        print(f"Error: {validated_type}")
        return

    is_valid, validated_description = validate_description(description)
    if not is_valid:
        print(f"Error: {validated_description}")
        return

    is_valid, validated_category = validate_category(category)
    if not is_valid:
        print(f"Error: {validated_category}")
        return
    if not is_valid_category(validated_category): # Updated call
        print(f"Error: Invalid category '{validated_category}'. Use 'finance category list' to see available categories.")
        return

    manager = TransactionManager()
    if manager.add_transaction(validated_amount, validated_date, validated_type, validated_description, validated_category):
        print("Transaction added successfully.")
    else:
        print("Error: Failed to add transaction.")

def edit():
    """Edits an existing financial transaction."""
    id = get_user_input('ID of the transaction to edit: ')
    amount = get_user_input('New amount of the transaction (leave empty to keep current): ')
    date_str = get_user_input('New date of the transaction (YYYY-MM-DD, leave empty to keep current): ')
    type_str = get_user_input('New type of the transaction (income/expense, leave empty to keep current): ')
    description = get_user_input('New description of the transaction (leave empty to keep current): ')
    category = get_user_input('New category of the transaction (leave empty to keep current): ')

    manager = TransactionManager()
    existing_transaction = manager.get_transaction(id)

    if not existing_transaction:
        print(f"Error: Transaction with ID '{id}' not found.")
        return

    updates = {}
    if amount:
        is_valid, validated_amount = validate_amount(amount)
        if not is_valid:
            print(f"Error: {validated_amount}")
            return
        updates['amount'] = validated_amount

    if date_str:
        is_valid, validated_date = validate_date(date_str)
        if not is_valid:
            print(f"Error: {validated_date}")
            return
        updates['date'] = validated_date

    if type_str:
        is_valid, validated_type = validate_type(type_str)
        if not is_valid:
            print(f"Error: {validated_type}")
            return
        updates['type'] = validated_type

    if description:
        is_valid, validated_description = validate_description(description)
        if not is_valid:
            print(f"Error: {validated_description}")
            return
        updates['description'] = validated_description

    if category:
        is_valid, validated_category = validate_category(category)
        if not is_valid:
            print(f"Error: {validated_category}")
            return
        if not is_valid_category(validated_category): # Updated call
            print(f"Error: Invalid category '{validated_category}'. Use 'finance category list' to see available categories.")
            return
        updates['category'] = validated_category

    if not updates:
        print("No updates provided.")
        return

    if manager.update_transaction(id, **updates):
        print(f"Transaction '{id}' updated successfully.")
    else:
        print(f"Error: Failed to update transaction '{id}'.")

def delete():
    """Deletes an existing financial transaction."""
    id = get_user_input('ID of the transaction to delete: ')
    
    confirm = get_user_input(f"Are you sure you want to delete transaction '{id}'? This action cannot be undone. (yes/no): ").lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        return

    manager = TransactionManager()
    if manager.delete_transaction(id):
        print(f"Transaction '{id}' deleted successfully.")
    else:
        print(f"Error: Transaction '{id}' not found or failed to delete.")
