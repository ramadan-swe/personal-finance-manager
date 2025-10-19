import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# src/utils/prompt_toolkit_utils.py
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

def display_menu(title, menu_items):
    clear_screen()
    print(title)
    for i, item in enumerate(menu_items):
        print(f"{i+1}. {item.label}")
    print("Q. Exit")
    if "main" not in title.lower():
        print("B. Back")

def get_user_input(prompt_message, hide_input=False):
    return prompt(prompt_message, is_password=hide_input)
