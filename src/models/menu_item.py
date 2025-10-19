# src/models/menu_item.py
import json
import os

class MenuItem:
    def __init__(self, id, label, action, help_text, parent_id=None):
        self.id = id
        self.label = label
        self.action = action  # Can be a command string or a reference to a sub-menu
        self.help_text = help_text
        self.parent_id = parent_id

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "action": self.action,
            "help_text": self.help_text,
            "parent_id": self.parent_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["label"], data["action"], data["help_text"], data.get("parent_id"))

class MenuItemPersistence:
    def __init__(self, storage_file="menu_items.json"):
        self.storage_file = storage_file
        self._load_menu_items()

    def _load_menu_items(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.menu_items = {item_data["id"]: MenuItem.from_dict(item_data) for item_data in data}
        else:
            self.menu_items = {}

    def _save_menu_items(self):
        with open(self.storage_file, 'w') as f:
            json.dump([item.to_dict() for item in self.menu_items.values()], f, indent=4)

    def create_menu_item(self, menu_item):
        if menu_item.id in self.menu_items:
            return False
        self.menu_items[menu_item.id] = menu_item
        self._save_menu_items()
        return True

    def get_menu_item(self, item_id):
        return self.menu_items.get(item_id)

    def get_all_menu_items(self):
        return list(self.menu_items.values())

    def update_menu_item(self, menu_item):
        if menu_item.id not in self.menu_items:
            return False
        self.menu_items[menu_item.id] = menu_item
        self._save_menu_items()
        return True

    def delete_menu_item(self, item_id):
        if item_id in self.menu_items:
            del self.menu_items[item_id]
            self._save_menu_items()
            return True
        return False
