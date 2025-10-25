# Menu configuration for the application
ALL_MENUS = {
    "main": {
        "label": "Main Menu",
        "items": [
            {"id": "view_transactions", "label": "View Transactions", "action": "command:view_transactions", "help_text": "View all recorded transactions"},
            {"id": "search_menu", "label": "Search & Filter", "action": "menu:search_filter", "help_text": "Search and filter transactions"},
            {"id": "add_transaction", "label": "Add Transaction", "action": "command:add_transaction", "help_text": "Add a new financial transaction"},
            {"id": "reports_menu", "label": "Reports", "action": "menu:reports", "help_text": "Access financial reports"},
            {"id": "savings_menu", "label": "Saving goal", "action": "menu:savings", "help_text": "Manage saving goals"},
            {"id": "settings_menu", "label": "Settings", "action": "menu:settings", "help_text": "Configure application settings"},
        ]
    },
    "reports": {
        "label": "Reports Menu",
        "items": [
            {"id": "monthly_report", "label": "Monthly Report", "action": "command:monthly_report", "help_text": "Generate monthly financial report"},
                {"id": "category_breakdown", "label": "Category Breakdown", "action": "command:category_breakdown", "help_text": "View spending by category"},
                {"id": "spending_trends", "label": "Spending Trends", "action": "command:spending_trends", "help_text": "View spending trends for the current month"},
        ]
    },
    "search_filter": {
        "label": "Search & Filter",
        "items": [
            {"id": "search_date_range", "label": "Search Transactions by Date Range", "action": "command:search_date_range", "help_text": "Search transactions by start and end date"},
            {"id": "filter_category", "label": "Filter Transactions by Category", "action": "command:filter_by_category", "help_text": "Show transactions for a given category"},
            {"id": "amount_range", "label": "Amount Range Filter", "action": "command:amount_range_filter", "help_text": "Filter transactions by amount range"},
        ]
    },
    "savings": {
        "label": "Saving Goals",
        "items": [
            {"id": "set_saving_goal", "label": "Set Saving Goal", "action": "command:set_saving_goal", "help_text": "Create or update a saving goal"},
            {"id": "view_saving_goals", "label": "View & Add Saving Goals", "action": "command:view_saving_goals", "help_text": "View existing saving goals and add new ones"},
        ]
    },
    "settings": {
        "label": "Settings Menu",
        "items": [
            {"id": "change_pin", "label": "Change PIN", "action": "command:change_pin", "help_text": "Change user PIN"},
            {"id": "update_profile", "label": "Update Profile", "action": "command:update_profile", "help_text": "Update current user's profile information"},
            {"id": "data_management", "label": "Data Management", "action": "menu:data_management", "help_text": "Export, import, or restore data"},
            {"id": "switch_account", "label": "Switch Account", "action": "command:switch_account", "help_text": "Switch to another user account"},
            {"id": "logout", "label": "Logout", "action": "command:logout", "help_text": "Log out the current user"},
        ]
    },
    "data_management": {
        "label": "Data Management",
        "items": [
            {"id": "export_data", "label": "Export Data", "action": "command:export_data", "help_text": "Export transactions to a file"},
            {"id": "import_data", "label": "Import Data", "action": "command:import_data", "help_text": "Import transactions from a file"},
            {"id": "restore_data", "label": "Restore from Backup", "action": "command:restore_data", "help_text": "Restore transactions from a backup"},
        ]
    }
}