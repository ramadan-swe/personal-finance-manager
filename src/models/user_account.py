# src/models/user_account.py
import json
import os

class UserAccount:
    def __init__(self, username, hashed_pin, salt, profile_info=None):
        self.username = username
        self.hashed_pin = hashed_pin
        self.salt = salt
        self.profile_info = profile_info if profile_info is not None else {}

    def to_dict(self):
        return {
            "username": self.username,
            "hashed_pin": self.hashed_pin,
            "salt": self.salt.hex(), # Convert bytes to hex string for serialization
            "profile_info": self.profile_info
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["username"], data["hashed_pin"], bytes.fromhex(data["salt"]), data.get("profile_info")) # Convert hex string back to bytes

class UserAccountPersistence:
    def __init__(self, storage_file="user_accounts.json"):
        self.storage_file = storage_file
        self.accounts = {}
        self._load_accounts()

    def _load_accounts(self):
        if os.path.exists(self.storage_file):
            if os.path.getsize(self.storage_file) > 0: # Check if file is not empty
                with open(self.storage_file, 'r') as f:
                    try:
                        data = json.load(f)
                        self.accounts = {username: UserAccount.from_dict(account_data) for username, account_data in data.items()}
                    except json.JSONDecodeError:
                        # Handle corrupted JSON file, e.g., log error and start with empty accounts
                        from src.utils.prompt_toolkit_utils import add_message
                        add_message("Warning: Corrupted user_accounts.json found. Starting with empty accounts.")
                        self.accounts = {}
            else:
                self.accounts = {}
        else:
            self.accounts = {}

    def _save_accounts(self):
        with open(self.storage_file, 'w') as f:
            json.dump({username: account.to_dict() for username, account in self.accounts.items()}, f, indent=4)

    def create_account(self, user_account):
        if user_account.username in self.accounts:
            return False # Account already exists
        self.accounts[user_account.username] = user_account
        self._save_accounts()
        return True

    def get_account(self, username):
        return self.accounts.get(username)

    def get_all_accounts(self):
        return list(self.accounts.values())

    def update_account(self, user_account):
        if user_account.username not in self.accounts:
            return False # Account does not exist
        self.accounts[user_account.username] = user_account
        self._save_accounts()
        return True

    def delete_account(self, username):
        if username in self.accounts:
            del self.accounts[username]
            self._save_accounts()
            return True
        return False