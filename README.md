# Personal Finance Manager

A comprehensive console-based personal finance management application built with Python. Track income, expenses, savings goals, and generate detailed financial reports with an intuitive menu-driven interface.

## How to Run the Program

### Prerequisites
- Python 3.10 or higher
- Poetry package manager (optional)
- Required packages: `prompt-toolkit`

### Installation
1. Clone or download the project
2. Navigate to the project directory
3. Install dependencies (if using Poetry):
   ```bash
   poetry install
   ```
   Or manually install prompt-toolkit:
   ```bash
   pip install prompt-toolkit
   ```

### Running the Application
```bash
python -m src.main
```

### First Time Setup
1. Run the application
2. Choose "Register" to create your first user account (or login if you've already registered)
3. Set up your PIN and profile information
4. Start adding transactions and managing your finances

## Feature List

### Core Features
- **Multi-User Support**: Create multiple user accounts with PIN protection
- **Transaction Management**: Add, view, edit, and delete income/expense transactions
- **Dashboard**: Real-time financial overview with balance and spending summary
- **Reports**: Monthly reports, category breakdowns, and spending trends
- **Search & Filter**: Find transactions by date range, category, or amount
- **Data Persistence**: Automatic saving with backup system

### Advanced Features Implemented
- **Savings Goals**: Set and track progress toward financial goals
- **ASCII Charts**: Visual spending trend charts
- **CSV Import/Export**: Bulk data operations
- **Financial Health Score**: Automated financial wellness assessment
- **Account Switching**: Switch between multiple user accounts
- **Profile Management**: Update user information and security settings

### Technical Features
- **Secure Authentication**: PIN-based user authentication with hashing
- **Precise Calculations**: Decimal-based monetary calculations (no floating-point errors)
- **Input Validation**: Comprehensive validation for all user inputs
- **Auto-Backup**: Automatic data backups with restore capability
- **Professional UI**: Formatted tables, menus, and ASCII art dashboard

## User Guide

### Getting Started
1. **Registration**: Create an account with username and PIN
2. **Login**: Use your credentials to access the system
3. **Dashboard**: View your financial overview on the main screen

### Managing Transactions
- **Add Transaction**: Choose type (income/expense), enter amount, date, category, and description
- **View Transactions**: See all transactions in a formatted table
- **Edit/Delete**: Modify or remove transactions with confirmation prompts

### Using Reports
- **Monthly Report**: View income, expenses, and savings for any month
- **Category Breakdown**: Analyze spending by category with percentages
- **Spending Trends**: Visual chart of daily spending patterns

### Search & Filter
- **Date Range**: Find transactions between specific dates
- **Category Filter**: View transactions for specific categories
- **Amount Range**: Filter by minimum and maximum amounts

### Savings Goals
- **Set Goals**: Create named savings targets with target amounts and dates
- **Track Progress**: Monitor savings progress with visual indicators
- **Add Contributions**: Record money added toward your goals

### Data Management
- **Export**: Save transactions to CSV or JSON files
- **Import**: Bulk import transactions from CSV/JSON files
- **Backup/Restore**: Automatic backups with manual restore options

### Settings
- **Change PIN**: Update your security PIN
- **Update Profile**: Modify account information
- **Switch Account**: Change between user accounts
- **Logout**: Securely exit the application

## Known Issues/Limitations

### Current Limitations
- **Single Currency**: Only supports USD currency format (though extensible)
- **Console Only**: No graphical user interface (by design)
- **No Encryption**: Data files are not encrypted (use at your own risk)

### Known Issues
- **Category Management**: Categories are predefined and cannot be customized
- **Large Datasets**: Performance may degrade with thousands of transactions
- **Backup Retention**: Only keeps last 5 backups automatically

### Future Enhancements
- Multi-currency support
- Custom category creation
- Data encryption
- Advanced analytics and budgeting
- Recurring transaction templates

### System Requirements
- **OS**: Linux, macOS, Windows
- **Python**: 3.10+
- **Memory**: Minimal (loads all data into RAM)
- **Storage**: ~1MB per 1000 transactions

### Troubleshooting
- **Import Errors**: Ensure CSV files have correct headers and data formats
- **Data Corruption**: Use backup restore feature if data files become corrupted
- **Performance Issues**: Consider archiving old transactions for large datasets

---

**Built with ❤️ for ITI Python Course**
