# src/services/user_management.py

from src.models.user_account import UserAccount, UserAccountPersistence
from src.utils.security import generate_salt, hash_pin, verify_pin

class UserManagementService:
    """
    Service for managing user accounts including registration, authentication, and profile updates.
    """

    def __init__(self):
        """
        Initialize the UserManagementService with persistence layer.
        """
        self.persistence = UserAccountPersistence()

    def register_user(self, username, pin):
        """
        Register a new user account.

        Args:
            username: Desired username
            pin: PIN for authentication

        Returns:
            bool: True if registration successful, False if username already exists
        """
        if self.persistence.get_account(username):
            return False  # User already exists

        salt = generate_salt()
        hashed_pin = hash_pin(pin, salt)
        user_account = UserAccount(username, hashed_pin, salt)
        return self.persistence.create_account(user_account)

    def authenticate_user(self, username, pin):
        """
        Authenticate a user with username and PIN.

        Args:
            username: User's username
            pin: User's PIN

        Returns:
            UserAccount or None: User account if authentication successful, None otherwise
        """
        user_account = self.persistence.get_account(username)
        if user_account and verify_pin(pin, user_account.hashed_pin, user_account.salt):
            return user_account
        return None

    def update_profile(self, user_account):
        """
        Update a user's profile information.

        Args:
            user_account: UserAccount object with updated profile_info

        Returns:
            bool: True if update successful, False otherwise
        """
        # The user_account object passed here should already have its profile_info updated
        # We just need to persist the changes.
        return self.persistence.update_account(user_account)

    def update_pin(self, user_account, new_pin):
        """
        Update a user's PIN.

        Args:
            user_account: UserAccount object to update
            new_pin: New PIN to set

        Returns:
            bool: True if update successful, False otherwise
        """
        salt = generate_salt()
        hashed_pin = hash_pin(new_pin, salt)
        user_account.hashed_pin = hashed_pin
        user_account.salt = salt
        return self.persistence.update_account(user_account)
