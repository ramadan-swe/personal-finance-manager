# src/services/category_manager.py

class CategoryManager:
    _categories = ["Food", "Transport", "Housing", "Entertainment", "Salary", "Investments", "Utilities", "Healthcare", "Education", "Miscellaneous"]

    @classmethod
    def get_categories(cls):
        return sorted(cls._categories)

    @classmethod
    def is_valid_category(cls, category):
        return category in cls._categories

    @classmethod
    def add_category(cls, category):
        if category not in cls._categories:
            cls._categories.append(category)
            cls._categories.sort()
            return True
        return False
