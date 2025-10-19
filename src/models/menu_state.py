# src/models/menu_state.py
import json
import os

class MenuState:
    def __init__(self, user_id, navigation_stack=None, selected_options=None):
        self.user_id = user_id
        self.navigation_stack = navigation_stack if navigation_stack is not None else []
        self.selected_options = selected_options if selected_options is not None else {}

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "navigation_stack": self.navigation_stack,
            "selected_options": self.selected_options
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["user_id"], data.get("navigation_stack"), data.get("selected_options"))

class MenuStatePersistence:
    def __init__(self, storage_file="menu_states.json"):
        self.storage_file = storage_file
        self._load_menu_states()

    def _load_menu_states(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.menu_states = {state_data["user_id"]: MenuState.from_dict(state_data) for state_data in data}
        else:
            self.menu_states = {}

    def _save_menu_states(self):
        with open(self.storage_file, 'w') as f:
            json.dump([state.to_dict() for state in self.menu_states.values()], f, indent=4)

    def create_menu_state(self, menu_state):
        if menu_state.user_id in self.menu_states:
            return False
        self.menu_states[menu_state.user_id] = menu_state
        self._save_menu_states()
        return True

    def get_menu_state(self, user_id):
        return self.menu_states.get(user_id)

    def update_menu_state(self, menu_state):
        if menu_state.user_id not in self.menu_states:
            return False
        self.menu_states[menu_state.user_id] = menu_state
        self._save_menu_states()
        return True

    def delete_menu_state(self, user_id):
        if user_id in self.menu_states:
            del self.menu_states[user_id]
            self._save_menu_states()
            return True
        return False
