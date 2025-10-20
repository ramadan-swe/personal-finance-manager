from datetime import datetime
from src.models.transaction import PaymentMethod, Currencies

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

def validate_payment_method(payment_method):
    try:
        return True, PaymentMethod(payment_method.lower())
    except ValueError:
        return False, f"Invalid payment method. Allowed values are: {[pm.value for pm in PaymentMethod]}."

def validate_currency(currency_short_name):
    currency = Currencies.from_short_name(currency_short_name.upper())
    if currency:
        return True, currency
    return False, f"Invalid currency. Allowed values are: {[c.short_name for c in Currencies.get_all()]}."
