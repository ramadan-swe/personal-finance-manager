# src/services/transaction_manager.py
from src.models.transaction import Transaction, TransactionPersistence

class TransactionManager:
    def __init__(self):
        self.persistence = TransactionPersistence()

    def add_transaction(self, amount, date, type, description, category):
        transaction = Transaction(amount, date, type, description, category)
        return self.persistence.create_transaction(transaction)

    def get_transaction(self, transaction_id):
        return self.persistence.get_transaction(transaction_id)

    def get_all_transactions(self):
        return self.persistence.get_all_transactions()

    def update_transaction(self, transaction_id, **kwargs):
        existing_transaction = self.persistence.get_transaction(transaction_id)
        if not existing_transaction:
            return False

        # Apply updates
        for key, value in kwargs.items():
            setattr(existing_transaction, key, value)
        
        return self.persistence.update_transaction(existing_transaction)

    def delete_transaction(self, transaction_id):
        return self.persistence.delete_transaction(transaction_id)
