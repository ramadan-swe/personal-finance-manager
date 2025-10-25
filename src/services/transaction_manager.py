from src.models.transaction import Transaction
from src.services.data_persistence import DataPersistenceService
from math import floor, log10

class TransactionManager:
    """
    Manages transaction operations including CRUD operations and data persistence.
    """

    def __init__(self, data_persistence_service: DataPersistenceService):
        """
        Initialize the TransactionManager with a data persistence service.

        Args:
            data_persistence_service: Service for persisting transaction data
        """
        self.data_persistence_service = data_persistence_service
        self.transactions = {}
        self._load_transactions()

    def _load_transactions(self):
        """
        Load transactions from persistent storage.
        """
        from src.models.transaction import Transaction
        loaded_data = self.data_persistence_service.load_data()
        self.transactions = {t['id']: Transaction.from_dict(t) for t in loaded_data}

    def _save_transactions(self):
        """
        Save current transactions to persistent storage.
        """
        self.data_persistence_service.save_data(list(self.transactions.values()))

    def _generate_next_id(self):
        """
        Generate the next available transaction ID.

        Returns:
            str: Next transaction ID in format TX001, TX002, etc.
        """
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
        return self.format_transaction_id(new_id_num)
    
    @classmethod
    def format_transaction_id(cls, transaction_id):
        """
        Format a transaction ID to ensure consistent TX prefix and padding.

        Args:
            transaction_id: ID to format (int or string)

        Returns:
            str: Formatted transaction ID
        """
        if type(transaction_id) == int or transaction_id.isdigit():
            transaction_id = int(transaction_id)
            num_digits = max(floor(log10(transaction_id)) + 1, 3)
            return f"TX{transaction_id:0{num_digits}d}"
        return transaction_id

    def add_transaction(self, amount, date, type, description, category, user_id, payment_method, currency):
        """
        Add a new transaction.

        Args:
            amount: Transaction amount
            date: Transaction date
            type: Transaction type ('income' or 'expense')
            description: Transaction description
            category: Transaction category
            user_id: User ID
            payment_method: Payment method
            currency: Transaction currency

        Returns:
            bool: True if successful, False if transaction ID already exists
        """
        transaction = Transaction(amount, date, type, description, category, user_id, payment_method, currency)
        transaction.id = self._generate_next_id()
        if transaction.id in self.transactions:
            return False
        self.transactions[transaction.id] = transaction
        self._save_transactions()
        return True

    def get_transaction(self, transaction_id):
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction ID to retrieve

        Returns:
            Transaction or None: The transaction if found
        """
        transaction_id = self.format_transaction_id(transaction_id)
        return self.transactions.get(transaction_id)

    def get_all_transactions(self, user_id):
        """
        Get all transactions for a specific user.

        Args:
            user_id: User ID to filter transactions

        Returns:
            list: List of Transaction objects for the user
        """
        return [t for t in self.transactions.values() if t.user_id == user_id]

    def update_transaction(self, transaction_id, **kwargs):
        """
        Update a transaction with new values.

        Args:
            transaction_id: ID of transaction to update
            **kwargs: Key-value pairs of fields to update

        Returns:
            bool: True if successful, False if transaction not found
        """
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
        """
        Delete a transaction by ID.

        Args:
            transaction_id: ID of transaction to delete

        Returns:
            bool: True if successful, False if transaction not found
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        del self.transactions[transaction.id]
        self._save_transactions()
        return True

    def import_transactions(self, transactions, user_id):
        """
        Import a list of transactions for a user.

        Args:
            transactions: List of Transaction objects to import
            user_id: User ID to assign to imported transactions

        Returns:
            tuple: (imported_count, skipped_count)
        """
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
        """
        Export transactions to a file.

        Args:
            transactions: List of Transaction objects to export
            format: Export format ('json' or 'csv')
            output_path: Path to output file

        Returns:
            tuple: (success, message)
        """
        return self.data_persistence_service.export_data(transactions, format, output_path)

    def import_data(self, format, input_path, user_id):
        """
        Import transactions from a file.

        Args:
            format: Import format ('json' or 'csv')
            input_path: Path to input file
            user_id: User ID to assign to imported transactions

        Returns:
            tuple: (success, message)
        """
        success, data = self.data_persistence_service.import_data(format, input_path, user_id)
        if not success:
            return success, data

        # Convert raw dicts to Transaction objects
        from src.models.transaction import Transaction
        transactions = [Transaction.from_dict(t) for t in data]
        imported_count, skipped_count = self.import_transactions(transactions, user_id)

        return True, f"Data imported successfully. {imported_count} transactions imported, {skipped_count} skipped."

    def get_backups(self):
        """
        Get list of available backup files.

        Returns:
            list: List of backup filenames
        """
        return self.data_persistence_service.get_backups()

    def restore_from_backup(self, backup_file):
        """
        Restore data from a backup file.

        Args:
            backup_file: Name of backup file to restore

        Returns:
            tuple: (success, message)
        """
        success, message = self.data_persistence_service.restore_from_backup(backup_file)
        if success:
            self._load_transactions() # Reload transactions after restoring
        return success, message
