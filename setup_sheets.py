"""
Google Sheets Database Setup Script for FinDash
Creates the 6-sheet schema with proper headers
"""

import gspread
from google.oauth2.service_account import Credentials
import sys

# Define the scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Service account file
SERVICE_ACCOUNT_FILE = 'my-streamlit-backend-1d5b2fadc28a.json'

def create_findash_sheets(spreadsheet_name="FinDash-DB"):
    """
    Creates a new Google Spreadsheet with the FinDash schema
    """
    try:
        # Authorize with service account
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)

        print(f"Creating spreadsheet: {spreadsheet_name}...")

        # Create new spreadsheet
        spreadsheet = client.create(spreadsheet_name)

        # Share with yourself (optional - replace with your email)
        # spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')

        print(f"✓ Spreadsheet created: {spreadsheet.url}")
        print(f"✓ Spreadsheet ID: {spreadsheet.id}")

        # Get the default sheet and rename it
        sheet1 = spreadsheet.sheet1
        sheet1.update_title("Users")

        # 1. Users Sheet
        print("\n Setting up Users sheet...")
        users_headers = [
            'user_id', 'full_name', 'email', 'hashed_password',
            'reset_token', 'token_expiry', 'created_at'
        ]
        sheet1.append_row(users_headers)
        sheet1.format('A1:G1', {'textFormat': {'bold': True}})

        # 2. User_Data Sheet
        print("✓ Setting up User_Data sheet...")
        user_data_sheet = spreadsheet.add_worksheet(
            title="User_Data",
            rows="1000",
            cols="10"
        )
        user_data_headers = [
            'user_id', 'simplefin_access_url', 'last_sync_time',
            'settings_json'
        ]
        user_data_sheet.append_row(user_data_headers)
        user_data_sheet.format('A1:D1', {'textFormat': {'bold': True}})

        # 3. User_Rules Sheet
        print("✓ Setting up User_Rules sheet...")
        rules_sheet = spreadsheet.add_worksheet(
            title="User_Rules",
            rows="1000",
            cols="10"
        )
        rules_headers = [
            'user_id', 'rule_id', 'priority', 'rule_field',
            'rule_condition', 'rule_value', 'rule_category', 'created_at'
        ]
        rules_sheet.append_row(rules_headers)
        rules_sheet.format('A1:H1', {'textFormat': {'bold': True}})

        # 4. Account_Balances Sheet
        print("✓ Setting up Account_Balances sheet...")
        balances_sheet = spreadsheet.add_worksheet(
            title="Account_Balances",
            rows="10000",
            cols="10"
        )
        balances_headers = [
            'user_id', 'date', 'account_name', 'balance',
            'account_type', 'account_id'
        ]
        balances_sheet.append_row(balances_headers)
        balances_sheet.format('A1:F1', {'textFormat': {'bold': True}})

        # 5. Budget_Monthly Sheet
        print("✓ Setting up Budget_Monthly sheet...")
        budget_sheet = spreadsheet.add_worksheet(
            title="Budget_Monthly",
            rows="1000",
            cols="10"
        )
        budget_headers = [
            'user_id', 'month_year', 'category', 'budgeted',
            'spent', 'last_updated'
        ]
        budget_sheet.append_row(budget_headers)
        budget_sheet.format('A1:F1', {'textFormat': {'bold': True}})

        # 6. Recurring_Templates Sheet
        print("✓ Setting up Recurring_Templates sheet...")
        templates_sheet = spreadsheet.add_worksheet(
            title="Recurring_Templates",
            rows="1000",
            cols="10"
        )
        templates_headers = [
            'user_id', 'template_id', 'description', 'amount',
            'category', 'frequency', 'created_at'
        ]
        templates_sheet.append_row(templates_headers)
        templates_sheet.format('A1:G1', {'textFormat': {'bold': True}})

        # 7. Transactions Sheet (for storing actual transactions)
        print("✓ Setting up Transactions sheet...")
        transactions_sheet = spreadsheet.add_worksheet(
            title="Transactions",
            rows="50000",
            cols="15"
        )
        transactions_headers = [
            'user_id', 'transaction_id', 'date', 'payee', 'amount',
            'category', 'account_name', 'account_id', 'notes',
            'pending', 'created_at', 'modified_at'
        ]
        transactions_sheet.append_row(transactions_headers)
        transactions_sheet.format('A1:L1', {'textFormat': {'bold': True}})

        print("\n" + "="*60)
        print("✓ SETUP COMPLETE!")
        print("="*60)
        print(f"\nSpreadsheet URL: {spreadsheet.url}")
        print(f"Spreadsheet ID: {spreadsheet.id}")
        print("\nIMPORTANT: Copy the Spreadsheet ID above and save it!")
        print("You'll need to add it to your config.py file.\n")

        return spreadsheet.id

    except Exception as e:
        print(f"\n✗ Error creating spreadsheet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_findash_sheets()
