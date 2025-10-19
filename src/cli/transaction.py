# src/cli/transaction.py
import click
from src.services.transaction_manager import TransactionManager
from src.models.transaction import Transaction
from src.utils.validators import validate_amount, validate_date, validate_type, validate_description, validate_category
from src.services.category_manager import CategoryManager

@click.group()
def transaction():
    """Manages financial transactions."""
    pass

@transaction.command()
@click.option('--amount', required=True, help='Amount of the transaction.')
@click.option('--date', required=True, help='Date of the transaction (YYYY-MM-DD).')
@click.option('--type', required=True, type=click.Choice(['income', 'expense'], case_sensitive=False), help='Type of the transaction (income/expense).')
@click.option('--description', required=True, help='Description of the transaction.')
@click.option('--category', required=True, help='Category of the transaction.')
def add(amount, date, type, description, category):
    """Adds a new financial transaction."""
    is_valid, validated_amount = validate_amount(amount)
    if not is_valid:
        click.echo(f"Error: {validated_amount}")
        return

    is_valid, validated_date = validate_date(date)
    if not is_valid:
        click.echo(f"Error: {validated_date}")
        return

    is_valid, validated_type = validate_type(type)
    if not is_valid:
        click.echo(f"Error: {validated_type}")
        return

    is_valid, validated_description = validate_description(description)
    if not is_valid:
        click.echo(f"Error: {validated_description}")
        return

    is_valid, validated_category = validate_category(category)
    if not is_valid:
        click.echo(f"Error: {validated_category}")
        return
    if not CategoryManager.is_valid_category(validated_category):
        click.echo(f"Error: Invalid category '{validated_category}'. Use 'finance category list' to see available categories.")
        return

    manager = TransactionManager()
    if manager.add_transaction(validated_amount, validated_date, validated_type, validated_description, validated_category):
        click.echo("Transaction added successfully.")
    else:
        click.echo("Error: Failed to add transaction.")

@transaction.command()
@click.option('--id', required=True, help='ID of the transaction to edit.')
@click.option('--amount', help='New amount of the transaction.')
@click.option('--date', help='New date of the transaction (YYYY-MM-DD).')
@click.option('--type', type=click.Choice(['income', 'expense'], case_sensitive=False), help='New type of the transaction (income/expense).')
@click.option('--description', help='New description of the transaction.')
@click.option('--category', help='New category of the transaction.')
def edit(id, amount, date, type, description, category):
    """Edits an existing financial transaction."""
    manager = TransactionManager()
    existing_transaction = manager.get_transaction(id)

    if not existing_transaction:
        click.echo(f"Error: Transaction with ID '{id}' not found.")
        return

    updates = {}
    if amount is not None:
        is_valid, validated_amount = validate_amount(amount)
        if not is_valid:
            click.echo(f"Error: {validated_amount}")
            return
        updates['amount'] = validated_amount

    if date is not None:
        is_valid, validated_date = validate_date(date)
        if not is_valid:
            click.echo(f"Error: {validated_date}")
            return
        updates['date'] = validated_date

    if type is not None:
        is_valid, validated_type = validate_type(type)
        if not is_valid:
            click.echo(f"Error: {validated_type}")
            return
        updates['type'] = validated_type

    if description is not None:
        is_valid, validated_description = validate_description(description)
        if not is_valid:
            click.echo(f"Error: {validated_description}")
            return
        updates['description'] = validated_description

    if category is not None:
        is_valid, validated_category = validate_category(category)
        if not is_valid:
            click.echo(f"Error: {validated_category}")
            return
        if not CategoryManager.is_valid_category(validated_category):
            click.echo(f"Error: Invalid category '{validated_category}'. Use 'finance category list' to see available categories.")
            return
        updates['category'] = validated_category

    if not updates:
        click.echo("No updates provided.")
        return

    if manager.update_transaction(id, **updates):
        click.echo(f"Transaction '{id}' updated successfully.")
    else:
        click.echo(f"Error: Failed to update transaction '{id}'.")

@transaction.command()
@click.option('--id', required=True, help='ID of the transaction to delete.')
def delete(id):
    """Deletes an existing financial transaction."""
    if not click.confirm(f"Are you sure you want to delete transaction '{id}'? This action cannot be undone."):
        click.echo("Deletion cancelled.")
        return

    manager = TransactionManager()
    if manager.delete_transaction(id):
        click.echo(f"Transaction '{id}' deleted successfully.")
    else:
        click.echo(f"Error: Transaction '{id}' not found or failed to delete.")

