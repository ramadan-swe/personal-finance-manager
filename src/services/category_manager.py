# src/services/category_manager.py

_categories = ["Food", "Transport", "Housing", "Entertainment", "Salary", "Investments", "Utilities", "Healthcare", "Education", "Miscellaneous", "Uncategorized"]

def get_categories():
    return sorted(_categories)

def is_valid_category(category):
    return category in _categories

