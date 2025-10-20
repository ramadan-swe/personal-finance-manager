from src.models.transaction import Transaction
from src.services.data_persistence import DataPersistenceService
from math import floor, log10

class TransactionManager:
    def __init__(self, data_persistence_service: DataPersistenceService):
        self.data_persistence_service = data_persistence_service
        self.transactions = {}
        self._load_transactions()

    def _load_transactions(self):
        loaded_transactions = self.data_persistence_service.load_data()
        self.transactions = {t.id: t for t in loaded_transactions}

    def _save_transactions(self):
        self.data_persistence_service.save_data(list(self.transactions.values()))

    def _generate_next_id(self):
        if not self.transactions:
            return "TX001"
        
        max_id = 0
        for tx_id in self.transactions.keys():
            if isinstance(tx_id, str) and tx_id.startswith("TX"):
                try:
                    num = int(tx_id[2:])
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue
        
        new_id_num = max_id + 1
        return self._convert_to_TX(new_id_num)
    
    @classmethod
    def _convert_to_TX(cls, transaction_id):
        if type(transaction_id) == int or transaction_id.isdigit():
            transaction_id = int(transaction_id)
            num_digits = max(floor(log10(transaction_id)) + 1, 3)
            return f"TX{transaction_id:0{num_digits}d}"
        return transaction_id

    def add_transaction(self, amount, date, type, description, category, user_id, payment_method, currency):
        transaction = Transaction(amount, date, type, description, category, user_id, payment_method, currency)
        transaction.id = self._generate_next_id()
        if transaction.id in self.transactions:
            return False
        self.transactions[transaction.id] = transaction
        self._save_transactions()
        return True

    def get_transaction(self, transaction_id):
        transaction_id = self._convert_to_TX(transaction_id)
        return self.transactions.get(transaction_id)

    def get_all_transactions(self, user_id):
        return [t for t in self.transactions.values() if t.user_id == user_id]

    def update_transaction(self, transaction_id, **kwargs):
        existing_transaction = self.get_transaction(transaction_id)
        if not existing_transaction:
            return False

        # Apply updates
        for key, value in kwargs.items():
            setattr(existing_transaction, key, value)
        
        self.transactions[existing_transaction.id] = existing_transaction
        self._save_transactions()
        return True

    def delete_transaction(self, transaction_id):
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        del self.transactions[transaction.id]
        self._save_transactions()
        return True

    def import_transactions(self, transactions, user_id):
        imported_count = 0
        skipped_count = 0
        for transaction in transactions:
            if transaction.id and self.get_transaction(transaction.id):
                skipped_count += 1
                continue
            
            if not transaction.id:
                transaction.id = self._generate_next_id()

            transaction.user_id = user_id # Assign user_id during import
            self.transactions[transaction.id] = transaction
            imported_count += 1
        
        self._save_transactions()
        return imported_count, skipped_count

    def export_data(self, transactions, format, output_path):
        return self.data_persistence_service.export_data(transactions, format, output_path)

    def import_data(self, format, input_path, user_id):
        return self.data_persistence_service.import_data(format, input_path, user_id)

    def get_backups(self):
        return self.data_persistence_service.get_backups()

    def restore_from_backup(self, backup_file):
        success, message = self.data_persistence_service.restore_from_backup(backup_file)
        if success:
            self._load_transactions() # Reload transactions after restoring
        return success, message
