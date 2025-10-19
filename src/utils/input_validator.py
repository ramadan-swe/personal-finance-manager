# src/utils/input_validator.py
import re
from datetime import datetime

def validate_username(username):
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters long."
    if ' ' in username:
        return False, "Username cannot contain spaces."
    return True, username

def validate_integer(value_str, min_val=None, max_val=None):
    try:
        value = int(value_str)
        if min_val is not None and value < min_val:
            return False, f"Value must be at least {min_val}."
        if max_val is not None and value > max_val:
            return False, f"Value must be at most {max_val}."
        return True, value
    except ValueError:
        return False, "Input must be an integer."

def validate_number(value_str, min_val=None, max_val=None):
    try:
        value = float(value_str)
        if min_val is not None and value < min_val:
            return False, f"Value must be at least {min_val}."
        if max_val is not None and value > max_val:
            return False, f"Value must be at most {max_val}."
        return True, value
    except ValueError:
        return False, "Input must be a number."

def validate_currency(value_str):
    # Allows optional $ sign, dot decimal, and up to two fraction digits
    match = re.fullmatch(r"^\$?\d+(\.\d{1,2})?$", value_str.strip())
    if match:
        try:
            # Convert to float, removing dollar sign if present
            amount = float(value_str.replace('$', ''))
            return True, amount
        except ValueError:
            return False, "Invalid currency format."
    return False, "Invalid currency format. Expected e.g., $12.34 or 12.34."

def validate_iso_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, date_str
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

def validate_pin(pin_str):
    if not re.fullmatch(r"^\d{6}$", pin_str):
        return False, "PIN must contain only 6 digits."
    return True, pin_str

def validate_yes_no(input_str):
    if input_str.lower() in ['y', 'yes']:
        return True, True
    if input_str.lower() in ['n', 'no']:
        return True, False
    return False, "Please enter 'y', 'yes', 'n', or 'no'."

def validate_category_name(name_str, max_len=64):
    if not re.fullmatch(r"^[a-zA-Z0-9\s\-]+$", name_str.strip()):
        return False, "Category name can only contain alphanumeric characters, spaces, and hyphens."
    if not (1 <= len(name_str.strip()) <= max_len):
        return False, f"Category name must be between 1 and {max_len} characters long."
    return True, name_str.strip()

def validate_free_text(text_str, max_len=1024):
    trimmed_text = text_str.strip()
    if not (1 <= len(trimmed_text) <= max_len):
        return False, f"Text must be between 1 and {max_len} characters long."
    return True, trimmed_text

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