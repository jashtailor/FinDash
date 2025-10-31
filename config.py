"""
Configuration file for FinDash
"""

import os

# =====================================
# Google Sheets Configuration
# =====================================
SERVICE_ACCOUNT_FILE = 'my-streamlit-backend-1d5b2fadc28a.json'
SPREADSHEET_ID = ''  # ADD YOUR SPREADSHEET ID HERE AFTER RUNNING setup_sheets.py

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# =====================================
# Sheet Names (Match the schema)
# =====================================
SHEET_USERS = 'Users'
SHEET_USER_DATA = 'User_Data'
SHEET_USER_RULES = 'User_Rules'
SHEET_ACCOUNT_BALANCES = 'Account_Balances'
SHEET_BUDGET_MONTHLY = 'Budget_Monthly'
SHEET_RECURRING_TEMPLATES = 'Recurring_Templates'
SHEET_TRANSACTIONS = 'Transactions'

# =====================================
# App Configuration
# =====================================
APP_NAME = "FinDash"
APP_ICON = "💰"
PAGE_TITLE = f"{APP_ICON} {APP_NAME}"

# Cache TTL (Time to Live) in seconds
CACHE_TTL = 300  # 5 minutes

# Default transaction display limit
DEFAULT_TRANSACTION_LIMIT = 60  # days

# =====================================
# Categories (Default)
# =====================================
DEFAULT_CATEGORIES = [
    "Uncategorized",
    "Income",
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Gas & Fuel",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Travel",
    "Personal Care",
    "Education",
    "Gifts & Donations",
    "Investments",
    "Transfer",
    "Other"
]

# Category Keywords for Auto-Categorization
CATEGORY_KEYWORDS = {
    "Income": ["salary", "paycheck", "deposit", "income", "payment received"],
    "Food & Dining": ["restaurant", "cafe", "starbucks", "mcdonald", "chipotle", "pizza", "uber eats", "doordash", "grubhub"],
    "Groceries": ["whole foods", "trader joe", "safeway", "kroger", "walmart", "target", "grocery", "market"],
    "Transportation": ["uber", "lyft", "taxi", "transit", "metro", "bus", "train", "parking"],
    "Gas & Fuel": ["shell", "chevron", "exxon", "mobil", "bp", "gas", "fuel"],
    "Shopping": ["amazon", "ebay", "etsy", "target", "walmart", "costco", "best buy"],
    "Entertainment": ["netflix", "spotify", "hulu", "disney", "movie", "theater", "steam", "playstation"],
    "Bills & Utilities": ["electric", "water", "internet", "phone", "verizon", "at&t", "comcast", "utility"],
    "Healthcare": ["pharmacy", "doctor", "hospital", "medical", "cvs", "walgreens", "health"],
    "Travel": ["airline", "hotel", "airbnb", "booking", "expedia", "flight"],
    "Personal Care": ["salon", "spa", "gym", "fitness", "haircut"],
    "Transfer": ["transfer", "venmo", "paypal", "zelle", "cash app"],
}

# =====================================
# Date Formats
# =====================================
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MONTH_YEAR_FORMAT = "%Y-%m"

# =====================================
# Session State Keys
# =====================================
SESSION_LOGGED_IN = 'logged_in'
SESSION_USER_ID = 'user_id'
SESSION_USER_EMAIL = 'user_email'
SESSION_USER_NAME = 'user_name'
SESSION_DATA_CACHE = 'data_cache'
SESSION_LAST_SYNC = 'last_sync'
