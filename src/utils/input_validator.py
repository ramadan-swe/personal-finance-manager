# src/utils/input_validator.py
import re
from datetime import datetime
from src.models.transaction import PaymentMethod, Currencies

# Validation constants
PIN_LENGTH = 6
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
DESCRIPTION_MAX_LENGTH = 255
CATEGORY_MAX_LENGTH = 64
FREE_TEXT_MAX_LENGTH = 1024

def validate_username(username):
    if not (USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH):
        return False, f"Username must be between {USERNAME_MIN_LENGTH} and {USERNAME_MAX_LENGTH} characters long."
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

def validate_currency_amount(value_str):
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
    if not re.fullmatch(rf"^\d{{{PIN_LENGTH}}}$", pin_str):
        return False, f"PIN must contain only {PIN_LENGTH} digits."
    return True, pin_str

def validate_category_name(name_str, max_len=CATEGORY_MAX_LENGTH):
    if not re.fullmatch(r"^[a-zA-Z0-9\s\-]+$", name_str.strip()):
        return False, "Category name can only contain alphanumeric characters, spaces, and hyphens."
    if not (1 <= len(name_str.strip()) <= max_len):
        return False, f"Category name must be between 1 and {max_len} characters long."
    return True, name_str.strip()

def validate_free_text(text_str, max_len=FREE_TEXT_MAX_LENGTH):
    trimmed_text = text_str.strip()
    if not (1 <= len(trimmed_text) <= max_len):
        return False, f"Text must be between 1 and {max_len} characters long."
    return True, trimmed_text

def validate_amount(amount):
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be positive."
        return True, amount
    except ValueError:
        return False, "Amount must be a number."

def validate_payment_method(payment_method):
    try:
        return True, PaymentMethod(payment_method.lower())
    except ValueError:
        return False, f"Invalid payment method. Allowed values are: {[pm.value for pm in PaymentMethod]}."

def validate_currency(currency_short_name):
    currency = Currencies.from_short_name(currency_short_name.upper())
    if currency:
        return True, currency
    return False, f"Invalid currency. Allowed values are: {[c.short_name for c in Currencies.get_currencies()]}."

def _get_validated_input(prompt, default_value=None, validator_func=None, allow_empty=False, allow_skip=False, is_edit_mode=False, display_current_or_default=True, error_message="Invalid input."):
    from src.utils.prompt_toolkit_utils import get_user_input, add_message, CANCEL_COMMAND
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

def validate_type(transaction_type):
    if transaction_type.lower() in ['income', 'expense']:
        return True, transaction_type.lower()
    return False, "Type must be 'income' or 'expense'."

def validate_description(description):
    if not isinstance(description, str) or not description.strip():
        return False, "Description cannot be empty."
    if len(description) > DESCRIPTION_MAX_LENGTH:
        return False, f"Description cannot exceed {DESCRIPTION_MAX_LENGTH} characters."
    return True, description.strip()

def validate_category(category):
    # For now, any non-empty string is a valid category. 
    # This will be enhanced when category_manager is implemented.
    if not isinstance(category, str) or not category.strip():
        return False, "Category cannot be empty."
    return True, category.strip()