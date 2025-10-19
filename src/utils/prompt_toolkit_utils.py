import os
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text # Import print_formatted_text

_messages = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def add_message(message, immediate=False):
    if immediate:
        print_formatted_text(message)
    else:
        _messages.append(message)

def display_messages():
    if _messages:
        for msg in _messages:
            print_formatted_text(msg)
        _messages.clear()
        print_formatted_text("-" * 20) # Separator

def display_menu(title, menu_items):
    clear_screen()
    display_messages() # Display accumulated messages before showing the menu

    print_formatted_text(title) # Use print_formatted_text
    for i, item in enumerate(menu_items):
        print_formatted_text(f"{i+1}. {item.get('label')}") # Use print_formatted_text
    print_formatted_text("Q. Exit") # Use print_formatted_text
    if "main" not in title.lower():
        print_formatted_text("B. Back") # Use print_formatted_text

def get_user_input(prompt_message, hide_input=False):
    return prompt(prompt_message, is_password=hide_input)
