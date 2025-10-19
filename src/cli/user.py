# src/cli/user.py
import click
from src.services.user_management import UserManagementService
from src.services.session_manager import SessionManager
import json

@click.group()
def user():
    """Manages user accounts and profiles."""
    pass

@user.command()
@click.option('--username', prompt='Enter username', help='The username for the new account.')
@click.option('--pin', prompt='Enter PIN', hide_input=True, confirmation_prompt=True, help='The PIN for the new account.')
def register(username, pin):
    """Registers a new user account."""
    service = UserManagementService()
    if service.register_user(username, pin):
        click.echo(f"User '{username}' registered successfully.")
    else:
        click.echo(f"Error: User '{username}' already exists or registration failed.")

@user.command()
@click.option('--username', prompt='Enter username', help='The username to log in with.')
@click.option('--pin', prompt='Enter PIN', hide_input=True, help='The PIN for the account.')
def login(username, pin):
    """Logs in a user."""
    service = UserManagementService()
    user_account = service.authenticate_user(username, pin)
    if user_account:
        SessionManager.login_user(user_account)
        click.echo(f"User '{username}' logged in successfully.")
    else:
        click.echo("Error: Invalid username or PIN.")

@user.command('update-profile')
@click.option('--name', help='New name for the profile.')
@click.option('--preferences', help='JSON string of preferences to update.')
def update_profile_command(name, preferences):
    """Updates the current user's profile information."""
    current_user = SessionManager.get_current_user()
    if not current_user:
        click.echo("Error: No user is currently logged in.")
        return

    service = UserManagementService()
    updated = False
    if name:
        current_user.profile_info['name'] = name
        updated = True
    if preferences:
        try:
            prefs = json.loads(preferences)
            current_user.profile_info.update(prefs)
            updated = True
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON format for preferences.")
            return

    if updated:
        if service.update_profile(current_user):
            click.echo("Profile updated successfully.")
        else:
            click.echo("Error: Failed to update profile.")
    else:
        click.echo("No updates provided.")

@user.command()
@click.option('--username', prompt='Enter username to switch to', help='The username of the account to switch to.')
@click.option('--pin', prompt='Enter PIN', hide_input=True, help='The PIN for the account.')
def switch(username, pin):
    """Switches to another user account."""
    service = UserManagementService()
    user_account = service.authenticate_user(username, pin)
    if user_account:
        SessionManager.login_user(user_account)
        click.echo(f"Switched to user '{username}' successfully.")
    else:
        click.echo("Error: Invalid username or PIN.")

@user.command()
def logout():
    """Logs out the current user."""
    if SessionManager.is_logged_in():
        username = SessionManager.get_current_user().username
        SessionManager.logout_user()
        click.echo(f"User '{username}' logged out successfully.")
    else:
        click.echo("No user is currently logged in.")