# src/utils/validators.py
from datetime import datetime

def validate_amount(amount):
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be positive."
        return True, amount
    except ValueError:
        return False, "Amount must be a number."

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, date_str
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

def validate_type(transaction_type):
    if transaction_type.lower() in ['income', 'expense']:
        return True, transaction_type.lower()
    return False, "Type must be 'income' or 'expense'."

def validate_description(description):
    if not isinstance(description, str) or not description.strip():
        return False, "Description cannot be empty."
    if len(description) > 255:
        return False, "Description cannot exceed 255 characters."
    return True, description.strip()

def validate_category(category):
    # For now, any non-empty string is a valid category. 
    # This will be enhanced when category_manager is implemented.
    if not isinstance(category, str) or not category.strip():
        return False, "Category cannot be empty."
    return True, category.strip()
