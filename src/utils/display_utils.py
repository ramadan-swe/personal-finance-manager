from src.utils.prompt_toolkit_utils import add_message

# Table column width constants
ID_COLUMN_WIDTH = 10
DATE_COLUMN_WIDTH = 12
TYPE_COLUMN_WIDTH = 8
CATEGORY_COLUMN_WIDTH = 25
AMOUNT_COLUMN_WIDTH = 12
DESCRIPTION_COLUMN_WIDTH = 40

def _display_transactions_table(transactions):
    # Reuse the same table formatting as _handle_view_transactions
    id_width = ID_COLUMN_WIDTH
    date_width = DATE_COLUMN_WIDTH
    type_width = TYPE_COLUMN_WIDTH
    category_width = CATEGORY_COLUMN_WIDTH
    amount_width = AMOUNT_COLUMN_WIDTH
    description_width = DESCRIPTION_COLUMN_WIDTH

    header = (f"{'ID':<{id_width}} | {'Date':<{date_width}} | {'Type':<{type_width}} | "
              f"{'Category':<{category_width}} | {'Amount':>{amount_width}} | {'Description':<{description_width}}")
    separator = "=" * (id_width + date_width + type_width + category_width + amount_width + description_width + (5 * 3))

    add_message(separator, immediate=True)
    add_message(header, immediate=True)
    add_message("-" * len(header), immediate=True)

    for t in transactions:
        display_id = str(t.id)[:id_width-3] + "..." if len(str(t.id)) > id_width else str(t.id)
        currency_symbol = getattr(t, 'currency', None)
        if currency_symbol and hasattr(currency_symbol, 'symbol'):
            symbol = currency_symbol.symbol
        else:
            symbol = '$'
        formatted_amount = f"{symbol}{t.amount:,.2f}"
        display_description = t.description[:description_width] + "..." if len(t.description) > description_width else t.description
        row = (f"{display_id:<{id_width}} | {t.date:<{date_width}} | {t.type:<{type_width}} | "
                f"{t.category:<{category_width}} | {formatted_amount:>{amount_width}} | {display_description:<{description_width}}")
        add_message(row, immediate=True)
    add_message(separator, immediate=True)