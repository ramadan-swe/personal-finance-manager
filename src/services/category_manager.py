# src/services/category_manager.py

_categories = ["Food", "Transport", "Housing", "Entertainment", "Salary", "Investments", "Utilities", "Healthcare", "Education", "Miscellaneous"]

def get_categories():
    return sorted(_categories)

def is_valid_category(category):
    return category in _categories

def add_category(category):
    global _categories
    if category not in _categories:
        _categories.append(category)
        _categories.sort()
        return True
    return False
