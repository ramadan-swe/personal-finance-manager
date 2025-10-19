# src/models/transaction.py
import json
import os
import uuid
from datetime import datetime

class Transaction:
    def __init__(self, amount, date, type, description, category, user_id, id=None):
        self.id = id if id else str(uuid.uuid4())
        self.amount = float(amount)
        self.date = date # Store as ISO format string YYYY-MM-DD
        self.type = type # "income" or "expense"
        self.description = description
        self.category = category
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "type": self.type,
            "description": self.description,
            "category": self.category,
            "user_id": self.user_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["amount"], data["date"], data["type"], data["description"], data["category"], data.get("user_id"), data["id"])

class TransactionPersistence:
    def __init__(self, storage_file="transactions.json"):
        self.storage_file = storage_file
        self._load_transactions()

    def _load_transactions(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.transactions = {t_data["id"]: Transaction.from_dict(t_data) for t_data in data}
        else:
            self.transactions = {}

    def _save_transactions(self):
        with open(self.storage_file, 'w') as f:
            json.dump([t.to_dict() for t in self.transactions.values()], f, indent=4)

    def create_transaction(self, transaction):
        if transaction.id in self.transactions:
            # This should ideally not happen with uuid4, but as a safeguard
            return False
        self.transactions[transaction.id] = transaction
        self._save_transactions()
        return True

    def get_transaction(self, transaction_id):
        return self.transactions.get(transaction_id)

    def get_all_transactions(self):
        return list(self.transactions.values())

    def update_transaction(self, transaction):
        if transaction.id not in self.transactions:
            return False
        self.transactions[transaction.id] = transaction
        self._save_transactions()
        return True

    def delete_transaction(self, transaction_id):
        if transaction_id in self.transactions:
            del self.transactions[transaction_id]
            self._save_transactions()
            return True
        return False
