💰 Personal Finance Manager
===========================

Python Console Application Project

10-Days | Due: \[24 Oct 2025\]

📋 Project Overview
-------------------

You will build a comprehensive console-based Personal Finance Manager that helps users track income, expenses, savings goals, and generate financial reports. This real-world application will demonstrate your mastery of Python fundamentals.

**🎯 What You'll Learn:**

*   Complex data structures and file handling
*   Menu-driven program architecture
*   Data validation and error handling
*   Financial calculations and reporting
*   Professional code organization

Core Requirements
-----------------

#### 👤 User Management

*   Multi-user support
*   PIN/password protection
*   User profiles
*   Profile switching

#### 💳 Transactions

*   Add income/expenses
*   View all transactions
*   Edit transactions
*   Delete with confirmation

#### 📊 Reports

*   Dashboard summary
*   Monthly reports
*   Category breakdown
*   Spending trends

#### 🔍 Search & Filter

*   Search by date range
*   Filter by category
*   Amount range filter
*   Sort results

#### 💾 Data Persistence

*   Save to CSV/JSON
*   Load on startup
*   Auto-save feature
*   Backup system

#### 🎛️ Menu System

*   Main menu
*   Sub-menus
*   Input validation
*   Help system

Advanced Features (Choose 4+ for full credit)
---------------------------------------------

### Available Advanced Features:

Savings Goals with Progress Tracking Monthly Budget Management Recurring Transactions ASCII Data Visualization Predictive Analytics CSV Import/Export Bill Reminders System Financial Health Score

**⚠️ Important:** You must implement at least 4 advanced features. Each feature should be fully functional, not partially implemented.

🔧 Technical Requirements
-------------------------

### Required Python Modules

import datetime # For date/time handling  
import csv # For CSV file operations  
import json # For JSON data storage  
import os # For file operations  
from decimal import Decimal # For accurate money calculations

### Required Data Structures

\# Transaction Structure  
transaction = {  

                    "transaction\_id": "TXN001",
                    "user\_id": "UUID",
                    "type": "expense",  # or "income"
                    "amount": 50.00,
                    "category": "Food",
                    "date": "2025-10-12",
                    "description": "Lunch at restaurant",
                    "payment\_method": "Credit Card"
                

}  
  
\# User Structure user = {

                                "user\_id": "UUID",
                                "name": "John Doe",
                                "password": "hashed\_password",
                                "currency": "USD"
                            

}

### Program Structure

*   **main.py** - Main program entry point with menu system
*   **Functions** - Minimum 10 well-defined functions
*   **Error Handling** - Use try/except blocks for file operations and user input
*   **Input Validation** - Validate all user inputs before processing
*   **Comments** - Every function must have a docstring

Sample Output
-------------

### Dashboard Example:

\# Sample Dashboard Output  

┌───────────────────────────────────────────────┐
│         PERSONAL FINANCE MANAGER v1.0         │
├───────────────────────────────────────────────┤
│ User: John Doe                                │
│ Period: October 2025                          │
├───────────────────────────────────────────────┤
│ Total Income:        $5,500.00                │
│ Total Expenses:      $3,420.50                │
│ Net Savings:         $2,079.50                │
├───────────────────────────────────────────────┤
│ Current Balance:     $15,650.75               │
└───────────────────────────────────────────────┘

Top Spending Categories:
1. Rent                 $1,200.00   (35.1%)
2. Food                 $650.00     (19.0%)
3. Transportation       $320.50     ( 9.4%)
					

### Transaction List Example:

\====================================================
ID     | Date      | Type   | Category | Amount
----------------------------------------------------
TXN001 | 2025-10-01 | Income  | Salary | $5,000.00
TXN002 | 2025-10-02 | Expense | Rent   | $1,200.00
TXN003 | 2025-10-05 | Expense | Food   | $45.50
====================================================
					

🗓️ 10-Day Timeline
-------------------

#### Days 1-2: Planning & Setup

*   Design program architecture and data structures
*   Create flowcharts for main features
*   Set up file structure and basic menu

#### Days 3-4: Core Features

*   User management (login/register)
*   Add transaction functionality
*   View transactions with formatting
*   Basic file I/O operations

#### Days 5-6: CRUD & Management

*   Edit and delete transactions
*   Category management system
*   Search and filter functionality
*   Complete data validation

#### Days 7-8: Reports & Advanced

*   Dashboard summary with calculations
*   Monthly and category reports
*   Implement 4 advanced features
*   Polish user interface

#### Days 9-10: Testing & Documentation

*   Comprehensive testing of all features
*   Bug fixes and error handling
*   Write complete documentation
*   Final polish and submission prep

Grading (100 Points)
--------------------

Category

Points

Requirements

Functionality

45

All core features working correctly

Advanced Features

20

4+ advanced features fully implemented

Code Quality

20

Functions, organization, error handling, comments

User Experience

10

Clear menus, formatted output, helpful messages

Documentation

5

README, code comments, testing document

**🎁 Bonus Opportunities (+10 points max):**

*   Exceptional UI with ASCII art (+3 points)
*   More than 4 advanced features (+4 points)
*   Video demo walkthrough (+3 points)

💡 Tips for Success
-------------------

**Start Simple**  
Get basic menu working first

**Test Often**  
Test each function immediately

**Use Functions**  
Break code into small pieces

**Validate Input**  
Check all user inputs

**Handle Errors**  
Use try/except blocks

**Keep Backups**  
Save working versions

**Read Errors**  
Error messages are helpful

**Ask for Help**  
Don't struggle for hours

### Common Pitfalls to Avoid:

*   ❌ Not validating user input (causes crashes)
*   ❌ Forgetting to save data after changes
*   ❌ Using float for money (use Decimal instead)
*   ❌ Not handling file not found errors
*   ❌ Too many nested if statements
*   ❌ Not testing with empty/invalid data
*   ❌ Leaving TODO comments in final submission

What to Submit
--------------

### Submission Checklist:

*   main.py (and any additional .py modules)
*   Sample data files (transactions.csv, users.json, etc.)
*   README.txt with:
    *   How to run the program
    *   Feature list
    *   User guide
    *   Known issues/limitations

**Submit Via:** \[Github\]

🎓 Academic Integrity
---------------------

**Important Guidelines:**

*   Teams are limited to **2 students per group**
*   You may discuss concepts with classmates but code must be your own
*   Using AI code generators for core functionality is not permitted
*   You may use AI for syntax help or debugging specific errors
*   Be prepared to explain any part of your code during evaluation
*   Cite any external resources or tutorials used

📚 Helpful Resources
--------------------

### Python Documentation:

*   datetime module: `https://docs.python.org/3/library/datetime.html`
*   csv module: `https://docs.python.org/3/library/csv.html`
*   json module: `https://docs.python.org/3/library/json.html`

### Concepts to Review:

*   File I/O (open, read, write, with statement)
*   Dictionary operations
*   List operations and list comprehensions
*   String formatting (f-strings)
*   Exception handling (try, except, finally)
*   Functions (parameters, return values, default arguments)

### 🚀 Ready to Build Something Amazing?

Remember: Every professional programmer started exactly where you are now. This project will challenge you, but you have all the skills needed to succeed. Take it one step at a time, test frequently. Good luck!