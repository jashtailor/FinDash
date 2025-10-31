"""
Database Manager for FinDash
Handles all Google Sheets operations with smart caching and batching
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

import config


@st.cache_resource
def get_gspread_client():
    """
    Get authenticated gspread client (cached per session)

    Returns:
        Authorized gspread client
    """
    try:
        creds = Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE,
            scopes=config.SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        return None


def get_spreadsheet():
    """
    Get the FinDash spreadsheet

    Returns:
        gspread Spreadsheet object
    """
    client = get_gspread_client()
    if not client:
        return None

    try:
        return client.open_by_key(config.SPREADSHEET_ID)
    except Exception as e:
        st.error(f"Failed to open spreadsheet: {e}")
        st.info("Make sure SPREADSHEET_ID is set in config.py")
        return None


# =====================================
# User Operations
# =====================================

def create_user(full_name: str, email: str, hashed_password: str) -> Optional[str]:
    """
    Create a new user in the Users sheet

    Args:
        full_name: User's full name
        email: User's email (must be unique)
        hashed_password: Bcrypt hashed password

    Returns:
        User ID if successful, None otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return None

        users_sheet = spreadsheet.worksheet(config.SHEET_USERS)

        # Check if email already exists
        emails = users_sheet.col_values(3)  # Column C (email)
        if email in emails[1:]:  # Skip header
            st.error("Email already exists")
            return None

        user_id = str(uuid.uuid4())
        created_at = datetime.now().strftime(config.DATETIME_FORMAT)

        # Append new user
        users_sheet.append_row([
            user_id,
            full_name,
            email,
            hashed_password,
            '',  # reset_token
            '',  # token_expiry
            created_at
        ])

        # Also create an entry in User_Data
        user_data_sheet = spreadsheet.worksheet(config.SHEET_USER_DATA)
        user_data_sheet.append_row([
            user_id,
            '',  # simplefin_access_url
            '',  # last_sync_time
            '{}'  # settings_json
        ])

        return user_id

    except Exception as e:
        st.error(f"Failed to create user: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user data by email

    Args:
        email: User's email

    Returns:
        Dictionary with user data, or None if not found
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return None

        users_sheet = spreadsheet.worksheet(config.SHEET_USERS)

        # Get all records
        records = users_sheet.get_all_records()

        for record in records:
            if record['email'] == email:
                return record

        return None

    except Exception as e:
        st.error(f"Failed to get user: {e}")
        return None


def update_reset_token(email: str, token: str, expiry: str) -> bool:
    """
    Update the password reset token for a user

    Args:
        email: User's email
        token: Reset token
        expiry: Token expiry datetime string

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        users_sheet = spreadsheet.worksheet(config.SHEET_USERS)

        # Find the user's row
        emails = users_sheet.col_values(3)  # Column C (email)

        try:
            row_index = emails.index(email) + 1
        except ValueError:
            return False

        # Update reset_token (column E) and token_expiry (column F)
        users_sheet.update_cell(row_index, 5, token)
        users_sheet.update_cell(row_index, 6, expiry)

        return True

    except Exception as e:
        st.error(f"Failed to update reset token: {e}")
        return False


# =====================================
# Transaction Operations
# =====================================

@st.cache_data(ttl=config.CACHE_TTL)
def load_user_transactions(_user_id: str) -> pd.DataFrame:
    """
    Load all transactions for a user (cached)

    Args:
        _user_id: User ID (prefixed with _ to prevent hashing)

    Returns:
        DataFrame with transactions
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return pd.DataFrame()

        transactions_sheet = spreadsheet.worksheet(config.SHEET_TRANSACTIONS)

        # Get all records
        records = transactions_sheet.get_all_records()

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Filter by user_id
        df = df[df['user_id'] == _user_id]

        # Convert date column to datetime
        if 'date' in df.columns and len(df) > 0:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Convert amount to numeric
        if 'amount' in df.columns and len(df) > 0:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        # Sort by date descending
        if len(df) > 0:
            df = df.sort_values('date', ascending=False)

        return df

    except Exception as e:
        st.error(f"Failed to load transactions: {e}")
        return pd.DataFrame()


def add_transaction(user_id: str, date: str, payee: str, amount: float,
                   category: str = "Uncategorized", account_name: str = "",
                   account_id: str = "", notes: str = "", pending: bool = False) -> bool:
    """
    Add a single transaction

    Args:
        user_id: User ID
        date: Transaction date (YYYY-MM-DD format)
        payee: Payee/merchant name
        amount: Transaction amount (negative for expenses)
        category: Category name
        account_name: Account name
        account_id: Account ID
        notes: Additional notes
        pending: Whether transaction is pending

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        transactions_sheet = spreadsheet.worksheet(config.SHEET_TRANSACTIONS)

        transaction_id = str(uuid.uuid4())
        created_at = datetime.now().strftime(config.DATETIME_FORMAT)

        transactions_sheet.append_row([
            user_id,
            transaction_id,
            date,
            payee,
            amount,
            category,
            account_name,
            account_id,
            notes,
            pending,
            created_at,
            created_at  # modified_at
        ])

        # Clear cache to force reload
        load_user_transactions.clear()

        return True

    except Exception as e:
        st.error(f"Failed to add transaction: {e}")
        return False


def batch_add_transactions(user_id: str, transactions: List[Dict[str, Any]]) -> bool:
    """
    Add multiple transactions in a single batch operation

    Args:
        user_id: User ID
        transactions: List of transaction dictionaries

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        transactions_sheet = spreadsheet.worksheet(config.SHEET_TRANSACTIONS)

        created_at = datetime.now().strftime(config.DATETIME_FORMAT)

        rows = []
        for txn in transactions:
            transaction_id = str(uuid.uuid4())
            rows.append([
                user_id,
                transaction_id,
                txn.get('date', ''),
                txn.get('payee', ''),
                txn.get('amount', 0),
                txn.get('category', 'Uncategorized'),
                txn.get('account_name', ''),
                txn.get('account_id', ''),
                txn.get('notes', ''),
                txn.get('pending', False),
                created_at,
                created_at
            ])

        # Batch append
        transactions_sheet.append_rows(rows)

        # Clear cache
        load_user_transactions.clear()

        return True

    except Exception as e:
        st.error(f"Failed to batch add transactions: {e}")
        return False


def update_transaction_category(transaction_id: str, category: str) -> bool:
    """
    Update the category of a transaction

    Args:
        transaction_id: Transaction ID
        category: New category name

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        transactions_sheet = spreadsheet.worksheet(config.SHEET_TRANSACTIONS)

        # Find the transaction
        transaction_ids = transactions_sheet.col_values(2)  # Column B

        try:
            row_index = transaction_ids.index(transaction_id) + 1
        except ValueError:
            st.error("Transaction not found")
            return False

        # Update category (column F) and modified_at (column L)
        modified_at = datetime.now().strftime(config.DATETIME_FORMAT)
        transactions_sheet.update_cell(row_index, 6, category)
        transactions_sheet.update_cell(row_index, 12, modified_at)

        # Clear cache
        load_user_transactions.clear()

        return True

    except Exception as e:
        st.error(f"Failed to update transaction: {e}")
        return False


def batch_update_transaction_categories(updates: List[tuple[str, str]]) -> bool:
    """
    Update categories for multiple transactions in batch

    Args:
        updates: List of (transaction_id, category) tuples

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        transactions_sheet = spreadsheet.worksheet(config.SHEET_TRANSACTIONS)

        # Get all transaction IDs
        transaction_ids = transactions_sheet.col_values(2)  # Column B

        modified_at = datetime.now().strftime(config.DATETIME_FORMAT)

        # Prepare batch update
        batch_updates = []
        for txn_id, category in updates:
            try:
                row_index = transaction_ids.index(txn_id) + 1
                batch_updates.append({
                    'range': f'F{row_index}',
                    'values': [[category]]
                })
                batch_updates.append({
                    'range': f'L{row_index}',
                    'values': [[modified_at]]
                })
            except ValueError:
                continue

        if batch_updates:
            transactions_sheet.batch_update(batch_updates)

        # Clear cache
        load_user_transactions.clear()

        return True

    except Exception as e:
        st.error(f"Failed to batch update categories: {e}")
        return False


# =====================================
# Rules Operations
# =====================================

@st.cache_data(ttl=config.CACHE_TTL)
def load_user_rules(_user_id: str) -> pd.DataFrame:
    """
    Load all categorization rules for a user (cached)

    Args:
        _user_id: User ID

    Returns:
        DataFrame with rules
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return pd.DataFrame()

        rules_sheet = spreadsheet.worksheet(config.SHEET_USER_RULES)

        records = rules_sheet.get_all_records()

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df = df[df['user_id'] == _user_id]

        # Sort by priority
        if len(df) > 0 and 'priority' in df.columns:
            df = df.sort_values('priority', ascending=True)

        return df

    except Exception as e:
        st.error(f"Failed to load rules: {e}")
        return pd.DataFrame()


def add_rule(user_id: str, rule_field: str, rule_condition: str,
            rule_value: str, rule_category: str, priority: int = 999) -> bool:
    """
    Add a categorization rule

    Args:
        user_id: User ID
        rule_field: Field to match (e.g., "payee")
        rule_condition: Condition (e.g., "contains", "equals")
        rule_value: Value to match
        rule_category: Category to assign
        priority: Rule priority (lower = higher priority)

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        rules_sheet = spreadsheet.worksheet(config.SHEET_USER_RULES)

        rule_id = str(uuid.uuid4())
        created_at = datetime.now().strftime(config.DATETIME_FORMAT)

        rules_sheet.append_row([
            user_id,
            rule_id,
            priority,
            rule_field,
            rule_condition,
            rule_value,
            rule_category,
            created_at
        ])

        # Clear cache
        load_user_rules.clear()

        return True

    except Exception as e:
        st.error(f"Failed to add rule: {e}")
        return False


# =====================================
# Budget Operations
# =====================================

@st.cache_data(ttl=config.CACHE_TTL)
def load_user_budgets(_user_id: str, month_year: Optional[str] = None) -> pd.DataFrame:
    """
    Load budgets for a user (cached)

    Args:
        _user_id: User ID
        month_year: Optional month filter (YYYY-MM format)

    Returns:
        DataFrame with budgets
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return pd.DataFrame()

        budget_sheet = spreadsheet.worksheet(config.SHEET_BUDGET_MONTHLY)

        records = budget_sheet.get_all_records()

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df = df[df['user_id'] == _user_id]

        if month_year:
            df = df[df['month_year'] == month_year]

        return df

    except Exception as e:
        st.error(f"Failed to load budgets: {e}")
        return pd.DataFrame()


def set_budget(user_id: str, month_year: str, category: str, budgeted: float) -> bool:
    """
    Set or update a budget for a category

    Args:
        user_id: User ID
        month_year: Month in YYYY-MM format
        category: Category name
        budgeted: Budgeted amount

    Returns:
        True if successful, False otherwise
    """
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return False

        budget_sheet = spreadsheet.worksheet(config.SHEET_BUDGET_MONTHLY)

        # Check if budget already exists
        records = budget_sheet.get_all_records()
        df = pd.DataFrame(records)

        existing = df[
            (df['user_id'] == user_id) &
            (df['month_year'] == month_year) &
            (df['category'] == category)
        ]

        last_updated = datetime.now().strftime(config.DATETIME_FORMAT)

        if len(existing) > 0:
            # Update existing
            row_index = existing.index[0] + 2  # +2 for header and 0-index
            budget_sheet.update_cell(row_index, 4, budgeted)
            budget_sheet.update_cell(row_index, 6, last_updated)
        else:
            # Create new
            budget_sheet.append_row([
                user_id,
                month_year,
                category,
                budgeted,
                0,  # spent (calculated separately)
                last_updated
            ])

        # Clear cache
        load_user_budgets.clear()

        return True

    except Exception as e:
        st.error(f"Failed to set budget: {e}")
        return False
