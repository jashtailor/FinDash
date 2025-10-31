"""
Utility functions for FinDash
"""

import pandas as pd
from typing import List, Tuple
import config


def auto_categorize_transaction(payee: str) -> str:
    """
    Auto-categorize a transaction based on payee using keyword matching

    Args:
        payee: Payee/merchant name

    Returns:
        Category name
    """
    if not payee:
        return "Uncategorized"

    payee_lower = payee.lower()

    # Check against keyword dictionary
    for category, keywords in config.CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in payee_lower:
                return category

    return "Uncategorized"


def apply_rule(transaction: pd.Series, rule: pd.Series) -> bool:
    """
    Check if a rule applies to a transaction

    Args:
        transaction: Transaction row
        rule: Rule row

    Returns:
        True if rule applies, False otherwise
    """
    field_value = str(transaction.get(rule['rule_field'], '')).lower()
    rule_value = str(rule['rule_value']).lower()
    condition = rule['rule_condition']

    if condition == 'contains':
        return rule_value in field_value
    elif condition == 'equals':
        return field_value == rule_value
    elif condition == 'starts_with':
        return field_value.startswith(rule_value)
    elif condition == 'ends_with':
        return field_value.endswith(rule_value)
    else:
        return False


def apply_rules_to_transactions(transactions_df: pd.DataFrame, rules_df: pd.DataFrame) -> List[Tuple[str, str]]:
    """
    Apply categorization rules to transactions

    Args:
        transactions_df: DataFrame of transactions
        rules_df: DataFrame of rules (sorted by priority)

    Returns:
        List of (transaction_id, category) tuples for batch update
    """
    updates = []

    for _, txn in transactions_df.iterrows():
        for _, rule in rules_df.iterrows():
            if apply_rule(txn, rule):
                # Only update if category changed
                if txn['category'] != rule['rule_category']:
                    updates.append((txn['transaction_id'], rule['rule_category']))
                break  # Stop at first matching rule (highest priority)

    return updates


def calculate_budget_progress(budgets_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate spending for each budget category

    Args:
        budgets_df: DataFrame of budgets
        transactions_df: DataFrame of transactions (filtered to relevant month)

    Returns:
        DataFrame with budgeted and spent columns
    """
    # Calculate spending by category (only negative amounts)
    spending = transactions_df[transactions_df['amount'] < 0].groupby('category')['amount'].sum()

    # Merge with budgets
    result = budgets_df.copy()
    result['spent'] = result['category'].map(spending).fillna(0)

    return result


def format_currency(amount: float) -> str:
    """
    Format a number as currency

    Args:
        amount: Amount to format

    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def validate_csv_format(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate CSV format for transaction import

    Args:
        df: DataFrame from uploaded CSV

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_columns = ['date', 'payee', 'amount']

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"

    # Check data types
    try:
        pd.to_datetime(df['date'], errors='raise')
    except Exception:
        return False, "Invalid date format in 'date' column"

    try:
        pd.to_numeric(df['amount'], errors='raise')
    except Exception:
        return False, "Invalid number format in 'amount' column"

    return True, ""


def get_month_name(month_year: str) -> str:
    """
    Convert YYYY-MM to readable month name

    Args:
        month_year: Month in YYYY-MM format

    Returns:
        Month name (e.g., "January 2025")
    """
    try:
        from datetime import datetime
        dt = datetime.strptime(month_year, config.MONTH_YEAR_FORMAT)
        return dt.strftime("%B %Y")
    except Exception:
        return month_year


def calculate_trend(current: float, previous: float) -> Tuple[float, str]:
    """
    Calculate percentage change and direction

    Args:
        current: Current period value
        previous: Previous period value

    Returns:
        Tuple of (percentage_change, direction)
    """
    if previous == 0:
        return 0.0, "neutral"

    change = ((current - previous) / abs(previous)) * 100

    if change > 0:
        direction = "up"
    elif change < 0:
        direction = "down"
    else:
        direction = "neutral"

    return abs(change), direction


def filter_transactions_by_date_range(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Filter transactions to last N days

    Args:
        df: DataFrame of transactions
        days: Number of days to include

    Returns:
        Filtered DataFrame
    """
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=days)
    return df[df['date'] >= cutoff_date]


def get_top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N merchants by total spending

    Args:
        df: DataFrame of transactions
        n: Number of top merchants to return

    Returns:
        DataFrame with merchant and total spending
    """
    # Only negative amounts (expenses)
    expenses = df[df['amount'] < 0].copy()
    expenses['amount'] = expenses['amount'].abs()

    top = expenses.groupby('payee')['amount'].sum().sort_values(ascending=False).head(n)

    return pd.DataFrame({
        'Merchant': top.index,
        'Total Spent': top.values
    })


def calculate_monthly_summary(df: pd.DataFrame, month_year: str) -> dict:
    """
    Calculate summary statistics for a month

    Args:
        df: DataFrame of all transactions
        month_year: Month in YYYY-MM format

    Returns:
        Dictionary with summary statistics
    """
    # Filter to month
    month_df = df[df['date'].dt.strftime(config.MONTH_YEAR_FORMAT) == month_year]

    if len(month_df) == 0:
        return {
            'income': 0,
            'expenses': 0,
            'net': 0,
            'transaction_count': 0,
            'avg_transaction': 0
        }

    income = month_df[month_df['amount'] > 0]['amount'].sum()
    expenses = abs(month_df[month_df['amount'] < 0]['amount'].sum())
    net = income - expenses
    count = len(month_df)
    avg = month_df['amount'].mean()

    return {
        'income': income,
        'expenses': expenses,
        'net': net,
        'transaction_count': count,
        'avg_transaction': avg
    }
