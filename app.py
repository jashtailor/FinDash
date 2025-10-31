"""
FinDash - Personal Finance Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

import config
import auth
import db_manager
from utils import (
    auto_categorize_transaction,
    apply_rules_to_transactions,
    calculate_budget_progress
)


# =====================================
# Page Configuration
# =====================================

st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================
# Initialize Session State
# =====================================

auth.init_session_state()


# =====================================
# Authentication Pages
# =====================================

def show_login_page():
    """Display the login page"""
    st.title(f"{config.APP_ICON} Welcome to {config.APP_NAME}")

    tab1, tab2, tab3 = st.tabs(["Sign In", "Sign Up", "Forgot Password"])

    # Sign In Tab
    with tab1:
        st.subheader("Sign In")

        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner("Signing in..."):
                        user = db_manager.get_user_by_email(email)

                        if user and auth.verify_password(password, user['hashed_password']):
                            auth.login_user(
                                user['user_id'],
                                user['email'],
                                user['full_name']
                            )
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")

    # Sign Up Tab
    with tab2:
        st.subheader("Create Account")

        with st.form("signup_form"):
            full_name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
            submit = st.form_submit_button("Sign Up", use_container_width=True)

            if submit:
                if not full_name or not email or not password or not password_confirm:
                    st.error("Please fill in all fields")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                elif not auth.validate_email(email):
                    st.error("Invalid email format")
                else:
                    is_valid, error_msg = auth.validate_password_strength(password)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        with st.spinner("Creating account..."):
                            hashed_password = auth.hash_password(password)
                            user_id = db_manager.create_user(full_name, email, hashed_password)

                            if user_id:
                                st.success("Account created successfully! Please sign in.")
                            else:
                                st.error("Failed to create account. Email may already exist.")

    # Forgot Password Tab
    with tab3:
        st.subheader("Reset Password")
        st.info("Password reset functionality requires email integration (GCP Function). This is a placeholder for Phase 4.")

        with st.form("forgot_password_form"):
            email = st.text_input("Email", key="forgot_email")
            submit = st.form_submit_button("Send Reset Link", use_container_width=True)

            if submit:
                if not email:
                    st.error("Please enter your email")
                else:
                    st.info("If this email exists, you'll receive a reset link shortly.")


# =====================================
# Main Dashboard
# =====================================

def show_dashboard():
    """Display the main dashboard"""
    st.title(f"{config.APP_ICON} {config.APP_NAME} Dashboard")

    # Load user data
    user_id = auth.get_current_user_id()
    user_name = auth.get_current_user_name()

    st.write(f"Welcome back, **{user_name}**!")

    # Load transactions
    with st.spinner("Loading transactions..."):
        transactions_df = db_manager.load_user_transactions(user_id)

    # Calculate metrics
    if len(transactions_df) > 0:
        # Filter to current month
        current_month = datetime.now().strftime(config.MONTH_YEAR_FORMAT)
        this_month_df = transactions_df[
            transactions_df['date'].dt.strftime(config.MONTH_YEAR_FORMAT) == current_month
        ]

        total_balance = transactions_df['amount'].sum()
        monthly_spending = this_month_df[this_month_df['amount'] < 0]['amount'].sum()
        monthly_income = this_month_df[this_month_df['amount'] > 0]['amount'].sum()
        transaction_count = len(this_month_df)

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Balance", f"${total_balance:,.2f}")

        with col2:
            st.metric("Monthly Spending", f"${abs(monthly_spending):,.2f}")

        with col3:
            st.metric("Monthly Income", f"${monthly_income:,.2f}")

        with col4:
            st.metric("Transactions", transaction_count)

        st.divider()

        # Spending by category (current month)
        if len(this_month_df) > 0:
            st.subheader("Spending by Category (This Month)")

            category_spending = this_month_df[this_month_df['amount'] < 0].groupby('category')['amount'].sum().abs()
            category_spending = category_spending.sort_values(ascending=False)

            if len(category_spending) > 0:
                fig = px.bar(
                    x=category_spending.index,
                    y=category_spending.values,
                    labels={'x': 'Category', 'y': 'Amount ($)'},
                    title="Spending by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No spending data for this month")

        st.divider()

        # Recent transactions
        st.subheader("Recent Transactions")
        display_df = transactions_df.head(10)[['date', 'payee', 'category', 'amount', 'account_name']]
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.info("No transactions yet. Upload a CSV file to get started!")


# =====================================
# Transactions Page
# =====================================

def show_transactions_page():
    """Display the transactions page with CSV upload and categorization"""
    st.title("Transactions")

    user_id = auth.get_current_user_id()

    # CSV Upload Section
    st.subheader("Import Transactions")

    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], help="Upload a CSV file with columns: date, payee, amount, account_name")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            st.write("Preview:")
            st.dataframe(df.head(), use_container_width=True)

            # Validate required columns
            required_cols = ['date', 'payee', 'amount']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                if st.button("Import Transactions", use_container_width=True):
                    with st.spinner("Importing transactions..."):
                        # Prepare transactions
                        transactions = []

                        for _, row in df.iterrows():
                            # Auto-categorize
                            category = auto_categorize_transaction(row['payee'])

                            txn = {
                                'date': row['date'],
                                'payee': row['payee'],
                                'amount': float(row['amount']),
                                'category': category,
                                'account_name': row.get('account_name', ''),
                                'account_id': row.get('account_id', ''),
                                'notes': row.get('notes', ''),
                                'pending': row.get('pending', False)
                            }
                            transactions.append(txn)

                        # Batch add
                        success = db_manager.batch_add_transactions(user_id, transactions)

                        if success:
                            st.success(f"Successfully imported {len(transactions)} transactions!")
                            st.rerun()
                        else:
                            st.error("Failed to import transactions")

        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

    st.divider()

    # Display all transactions
    st.subheader("All Transactions")

    with st.spinner("Loading transactions..."):
        transactions_df = db_manager.load_user_transactions(user_id)

    if len(transactions_df) > 0:
        # Add filters
        col1, col2 = st.columns(2)

        with col1:
            categories = ['All'] + sorted(transactions_df['category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)

        with col2:
            date_range = st.slider(
                "Date Range (days ago)",
                min_value=7,
                max_value=365,
                value=config.DEFAULT_TRANSACTION_LIMIT,
                step=7
            )

        # Apply filters
        cutoff_date = datetime.now() - timedelta(days=date_range)
        filtered_df = transactions_df[transactions_df['date'] >= cutoff_date]

        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]

        st.write(f"Showing {len(filtered_df)} transactions")

        # Display transactions
        display_df = filtered_df[['date', 'payee', 'category', 'amount', 'account_name', 'transaction_id']]
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')

        st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.info("No transactions found. Upload a CSV to get started!")


# =====================================
# Categorization Page
# =====================================

def show_categorization_page():
    """Display the manual categorization page"""
    st.title("Categorize Transactions")

    user_id = auth.get_current_user_id()

    with st.spinner("Loading transactions..."):
        transactions_df = db_manager.load_user_transactions(user_id)

    if len(transactions_df) > 0:
        # Filter uncategorized
        uncategorized = transactions_df[transactions_df['category'] == 'Uncategorized']

        st.write(f"**{len(uncategorized)}** uncategorized transactions")

        if len(uncategorized) > 0:
            st.subheader("Categorize One by One")

            # Display first uncategorized transaction
            txn = uncategorized.iloc[0]

            st.write(f"**Date:** {txn['date'].strftime('%Y-%m-%d')}")
            st.write(f"**Payee:** {txn['payee']}")
            st.write(f"**Amount:** ${txn['amount']:,.2f}")

            # Category selector
            category = st.selectbox(
                "Select Category",
                config.DEFAULT_CATEGORIES,
                key=f"cat_{txn['transaction_id']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Save Category", use_container_width=True):
                    success = db_manager.update_transaction_category(txn['transaction_id'], category)

                    if success:
                        st.success("Category updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update category")

            with col2:
                if st.button("Skip", use_container_width=True):
                    st.info("Skipped")
                    st.rerun()

        else:
            st.success("All transactions are categorized!")

    else:
        st.info("No transactions yet.")


# =====================================
# Budgets Page
# =====================================

def show_budgets_page():
    """Display the budgets page"""
    st.title("Monthly Budgets")

    user_id = auth.get_current_user_id()
    current_month = datetime.now().strftime(config.MONTH_YEAR_FORMAT)

    st.subheader(f"Budget for {current_month}")

    # Set budgets
    with st.expander("Set Budget", expanded=False):
        with st.form("budget_form"):
            category = st.selectbox("Category", config.DEFAULT_CATEGORIES[1:])  # Skip "Uncategorized"
            amount = st.number_input("Budget Amount", min_value=0.0, step=10.0)
            submit = st.form_submit_button("Save Budget", use_container_width=True)

            if submit:
                if amount > 0:
                    success = db_manager.set_budget(user_id, current_month, category, amount)

                    if success:
                        st.success("Budget saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save budget")
                else:
                    st.error("Amount must be greater than 0")

    # Load budgets
    with st.spinner("Loading budgets..."):
        budgets_df = db_manager.load_user_budgets(user_id, current_month)
        transactions_df = db_manager.load_user_transactions(user_id)

    if len(budgets_df) > 0:
        # Calculate spending
        this_month_df = transactions_df[
            transactions_df['date'].dt.strftime(config.MONTH_YEAR_FORMAT) == current_month
        ]

        budget_progress = calculate_budget_progress(budgets_df, this_month_df)

        # Display budget progress
        for _, budget in budget_progress.iterrows():
            category = budget['category']
            budgeted = budget['budgeted']
            spent = abs(budget['spent'])
            remaining = budgeted - spent
            percent = (spent / budgeted * 100) if budgeted > 0 else 0

            st.write(f"**{category}**")

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.progress(min(percent / 100, 1.0))

            with col2:
                st.write(f"${spent:,.2f} / ${budgeted:,.2f}")

            with col3:
                if remaining >= 0:
                    st.write(f"${remaining:,.2f} left")
                else:
                    st.write(f"${abs(remaining):,.2f} over", help="Over budget!")

            st.divider()

    else:
        st.info("No budgets set for this month. Set a budget above to get started!")


# =====================================
# Rules Page
# =====================================

def show_rules_page():
    """Display the categorization rules page"""
    st.title("Categorization Rules")

    user_id = auth.get_current_user_id()

    st.info("Rules are applied in priority order (1 = highest priority)")

    # Add new rule
    with st.expander("Add New Rule", expanded=False):
        with st.form("rule_form"):
            col1, col2 = st.columns(2)

            with col1:
                rule_field = st.selectbox("Field", ["payee", "amount"])
                rule_condition = st.selectbox("Condition", ["contains", "equals", "starts_with", "ends_with"])

            with col2:
                rule_value = st.text_input("Value")
                rule_category = st.selectbox("Category", config.DEFAULT_CATEGORIES)

            priority = st.number_input("Priority", min_value=1, value=999, step=1)

            submit = st.form_submit_button("Add Rule", use_container_width=True)

            if submit:
                if not rule_value:
                    st.error("Value is required")
                else:
                    success = db_manager.add_rule(
                        user_id, rule_field, rule_condition,
                        rule_value, rule_category, priority
                    )

                    if success:
                        st.success("Rule added!")
                        st.rerun()
                    else:
                        st.error("Failed to add rule")

    # Display existing rules
    st.subheader("Existing Rules")

    with st.spinner("Loading rules..."):
        rules_df = db_manager.load_user_rules(user_id)

    if len(rules_df) > 0:
        display_rules = rules_df[['priority', 'rule_field', 'rule_condition', 'rule_value', 'rule_category']]
        st.dataframe(display_rules, use_container_width=True, hide_index=True)

        # Apply rules button
        if st.button("Apply Rules to All Transactions", use_container_width=True):
            with st.spinner("Applying rules..."):
                transactions_df = db_manager.load_user_transactions(user_id)
                updates = apply_rules_to_transactions(transactions_df, rules_df)

                if len(updates) > 0:
                    success = db_manager.batch_update_transaction_categories(updates)

                    if success:
                        st.success(f"Applied rules to {len(updates)} transactions!")
                        st.rerun()
                    else:
                        st.error("Failed to apply rules")
                else:
                    st.info("No transactions needed rule updates")

    else:
        st.info("No rules defined yet. Add a rule above to get started!")


# =====================================
# Main App Logic
# =====================================

def main():
    """Main application logic"""

    # Check if user is logged in
    if not auth.is_logged_in():
        show_login_page()
        return

    # Sidebar navigation
    with st.sidebar:
        st.title(f"{config.APP_ICON} {config.APP_NAME}")
        st.write(f"Logged in as: **{auth.get_current_user_email()}**")

        st.divider()

        page = st.radio(
            "Navigation",
            ["Dashboard", "Transactions", "Categorize", "Budgets", "Rules"],
            label_visibility="collapsed"
        )

        st.divider()

        if st.button("Logout", use_container_width=True):
            auth.logout_user()
            st.rerun()

    # Display selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Transactions":
        show_transactions_page()
    elif page == "Categorize":
        show_categorization_page()
    elif page == "Budgets":
        show_budgets_page()
    elif page == "Rules":
        show_rules_page()


if __name__ == "__main__":
    main()
