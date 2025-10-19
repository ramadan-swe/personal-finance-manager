# src/services/session_manager.py

class SessionManager:
    _current_user = None

    @classmethod
    def login_user(cls, user_account):
        cls._current_user = user_account

    @classmethod
    def logout_user(cls):
        cls._current_user = None

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        return cls._current_user is not None
