from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
from src.utils.prompt_toolkit_utils import get_user_input
import json
from src.utils.prompt_toolkit_utils import add_message # Import add_message

def register():
    """Registers a new user account."""
    username = get_user_input('Enter desired username: ')
    pin = get_user_input('Enter PIN: ', hide_input=True)
    pin_confirm = get_user_input('Confirm PIN: ', hide_input=True)

    if pin != pin_confirm:
        add_message("PINs do not match. Please try again.")
        return False # Return False on failure

    service = UserManagementService()
    if service.register_user(username, pin):
        add_message(f"User '{username}' registered successfully.")
        return True # Return True on success
    else:
        add_message(f"Error: User '{username}' already exists or registration failed.")
        return False # Return False on failure

def login():
    """Logs in a user."""
    username = get_user_input('Enter username: ')
    pin = get_user_input('Enter PIN: ', hide_input=True)

    service = UserManagementService()
    user_account = service.authenticate_user(username, pin)
    if user_account:
        SessionManager.login_user(user_account)
        add_message(f"User '{username}' logged in successfully.")
        return True # Return True on success
    else:
        add_message("Error: Invalid username or PIN.")
        return False # Return False on failure

def update_profile_command():
    """Updates the current user's profile information."""
    current_user = SessionManager.get_current_user()
    if not current_user:
        add_message("Error: No user is currently logged in.")
        return

    name = get_user_input('New name for the profile (leave empty to skip): ')
    preferences_str = get_user_input('JSON string of preferences to update (leave empty to skip): ')

    service = UserManagementService()
    updated = False
    if name:
        current_user.profile_info['name'] = name
        updated = True
    if preferences_str:
        try:
            prefs = json.loads(preferences_str)
            current_user.profile_info.update(prefs)
            updated = True
        except json.JSONDecodeError:
            add_message("Error: Invalid JSON format for preferences.")
            return

    if updated:
        if service.update_profile(current_user):
            add_message("Profile updated successfully.")
        else:
            add_message("Error: Failed to update profile.")
    else:
        add_message("No updates provided.")

def switch():
    """Switches to another user account."""
    username = get_user_input('Enter username to switch to: ')
    pin = get_user_input('Enter PIN: ', hide_input=True)

    service = UserManagementService()
    user_account = service.authenticate_user(username, pin)
    if user_account:
        SessionManager.login_user(user_account)
        add_message(f"Switched to user '{username}' successfully.")
    else:
        add_message("Error: Invalid username or PIN.")

def logout():
    """Logs out the current user."""
    if SessionManager.is_logged_in():
        current_user = SessionManager.get_current_user()
        if current_user: # Ensure current_user is not None before accessing its attributes
            add_message(f"User '{current_user.username}' logged out successfully.")
        SessionManager.logout_user() # Always attempt to log out, even if current_user was None unexpectedly
    else:
        add_message("No user is currently logged in.")