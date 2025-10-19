# src/services/user_management.py

from src.models.user_account import UserAccount, UserAccountPersistence
from src.utils.security import generate_salt, hash_pin, verify_pin

class UserManagementService:
    def __init__(self):
        self.persistence = UserAccountPersistence()

    def register_user(self, username, pin):
        if self.persistence.get_account(username):
            return False  # User already exists

        salt = generate_salt()
        hashed_pin = hash_pin(pin, salt)
        user_account = UserAccount(username, hashed_pin, salt)
        return self.persistence.create_account(user_account)

    def authenticate_user(self, username, pin):
        user_account = self.persistence.get_account(username)
        if user_account and verify_pin(pin, user_account.hashed_pin, user_account.salt):
            return user_account
        return None

    def update_profile(self, user_account):
        # The user_account object passed here should already have its profile_info updated
        # We just need to persist the changes.
        return self.persistence.update_account(user_account)