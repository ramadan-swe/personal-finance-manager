import os
import json
import csv
from datetime import datetime
from dataclasses import dataclass # Import dataclass
from src.utils.file_utils import atomic_write

@dataclass
class DataFile:
    format: str
    created_at: datetime
    size: int
    checksum: str

@dataclass
class Backup:
    timestamp: datetime
    data_file_path: str

@dataclass
class AutoSaveJob:
    last_run: datetime
    status: str
    errors: str

# Backup management constants
MAX_BACKUPS = 5

class DataPersistenceService:
    def __init__(self, data_file="transactions.json", backup_dir="backups"):
        self.data_file = data_file
        self.backup_dir = backup_dir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)



    def save_data(self, transactions):
        """
        Saves transaction data to the data file.
        """
        # Local import to break circular dependency
        from src.models.transaction import Transaction
        data_to_save = [t.to_dict() for t in transactions]
        json_data = json.dumps(data_to_save, indent=4)
        atomic_write(self.data_file, json_data)
        self.create_backup()
        self.prune_backups()

    def export_data(self, transactions, format, output_path):
        """
        Exports data to CSV or JSON format.
        """
        # Local import to break circular dependency
        from src.models.transaction import Transaction
        if format == 'json':
            data_to_save = [t.to_dict() for t in transactions]
            json_data = json.dumps(data_to_save, indent=4)
            atomic_write(output_path, json_data)
            return True, "Data exported successfully."
        elif format == 'csv':
            if not transactions:
                return False, "No transactions to export."
            
            try:
                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=transactions[0].to_dict(target='csv').keys())
                    writer.writeheader()
                    for t in transactions:
                        writer.writerow(t.to_dict(target='csv'))
                return True, "Data exported successfully to CSV."
            except Exception as e:
                return False, f"Error exporting to CSV: {e}"
        else:
            return False, "Unsupported format."

    def import_data(self, format, input_path, user_id):
        """
        Imports data from CSV or JSON format.
        Returns raw dictionaries instead of Transaction objects.
        """
        if format == 'json':
            if not os.path.exists(input_path):
                return False, "File not found."
            with open(input_path, 'r') as f:
                try:
                    data = json.load(f)
                    return True, data
                except json.JSONDecodeError:
                    return False, "Invalid JSON format."
        elif format == 'csv':
            if not os.path.exists(input_path):
                return False, "File not found."

            try:
                with open(input_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = [row for row in reader]
                return True, data
            except Exception as e:
                return False, f"Error importing from CSV: {e}"
        else:
            return False, "Unsupported format."

    def create_backup(self):
        """
        Creates a timestamped backup of the data file.
        """
        if not os.path.exists(self.data_file):
            return

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file_name = f"transactions_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_file_name)
        
        with open(self.data_file, 'r') as f:
            data = f.read()
        
        atomic_write(backup_path, data)

    def prune_backups(self):
        """
        Prunes old backups to maintain MAX_BACKUPS backups.
        """
        backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith("transactions_") and f.endswith(".json")]

        if len(backup_files) <= MAX_BACKUPS:
            return

        backup_files.sort()

        files_to_delete = backup_files[:-MAX_BACKUPS]
        
        for file_to_delete in files_to_delete:
            os.remove(os.path.join(self.backup_dir, file_to_delete))

    def get_backups(self):
        """
        Returns a list of available backup files.
        """
        backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith("transactions_") and f.endswith(".json")]
        backup_files.sort(reverse=True)
        return backup_files

    def restore_from_backup(self, backup_file):
        """
        Restores data from a backup.
        """
        backup_path = os.path.join(self.backup_dir, backup_file)
        if not os.path.exists(backup_path):
            return False, "Backup file not found."

        with open(backup_path, 'r') as f:
            data = f.read()
            
        atomic_write(self.data_file, data)
        return True, "Data restored successfully."

    def load_data(self):
        """
        Loads transaction data from the data file.
        Returns raw dictionaries instead of Transaction objects.
        """
        if not os.path.exists(self.data_file):
            return []

        with open(self.data_file, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                # Handle corrupted file. For now, return empty list.
                from src.utils.prompt_toolkit_utils import add_message
                add_message(f"Warning: Corrupted data file {self.data_file}. Returning empty transactions.")
                return []