# 💰 FinDash - Personal Finance Dashboard

A secure, fast, and mobile-friendly personal finance dashboard built with Streamlit and Google Sheets.

## Features (Phase 1)

- ✅ **Secure Authentication** - Sign up, sign in with bcrypt password hashing
- ✅ **Transaction Management** - Import transactions via CSV, view and filter
- ✅ **Smart Categorization** - Auto-categorize transactions with keyword matching
- ✅ **Manual Categorization** - Manually categorize transactions one by one
- ✅ **Budget Tracking** - Set monthly budgets and track spending
- ✅ **Categorization Rules** - Create custom rules for automatic categorization
- ✅ **Dashboard Analytics** - View spending trends and summaries
- ✅ **Smart Caching** - Optimized performance with intelligent data caching

## Architecture

- **Frontend**: Streamlit
- **Backend Database**: Google Sheets (via gspread)
- **Authentication**: bcrypt + session state
- **Data Processing**: pandas (all in-memory)

## Project Structure

```
PF_v2/
├── app.py                          # Main Streamlit application
├── auth.py                         # Authentication functions
├── db_manager.py                   # Google Sheets operations
├── utils.py                        # Helper functions
├── config.py                       # Configuration settings
├── setup_sheets.py                 # Database setup script
├── requirements.txt                # Python dependencies
├── my-streamlit-backend-*.json     # Google service account credentials
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
└── README.md                       # This file
```

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. Google Cloud Platform account
3. Google Service Account with Sheets API access

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Google Sheets Database

1. Run the setup script to create your Google Sheets database:

```bash
python setup_sheets.py
```

2. Copy the **Spreadsheet ID** from the output
3. Open `config.py` and paste the ID into the `SPREADSHEET_ID` variable:

```python
SPREADSHEET_ID = 'your-spreadsheet-id-here'
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Guide

### 1. Create an Account

- Click on the "Sign Up" tab
- Enter your full name, email, and a strong password
- Password requirements:
  - At least 8 characters
  - One uppercase letter
  - One lowercase letter
  - One number

### 2. Import Transactions

- Navigate to the "Transactions" page
- Upload a CSV file with columns: `date`, `payee`, `amount`
- Optional columns: `account_name`, `account_id`, `notes`, `pending`
- Transactions will be automatically categorized using keyword matching

### 3. Categorize Transactions

- Go to the "Categorize" page
- Review uncategorized transactions one by one
- Select a category from the dropdown
- Click "Save Category" or "Skip"

### 4. Create Categorization Rules

- Navigate to the "Rules" page
- Click "Add New Rule"
- Define:
  - Field to match (e.g., "payee")
  - Condition (e.g., "contains")
  - Value to match (e.g., "Starbucks")
  - Category to assign (e.g., "Food & Dining")
  - Priority (lower number = higher priority)
- Click "Apply Rules to All Transactions" to batch categorize

### 5. Set Monthly Budgets

- Go to the "Budgets" page
- Click "Set Budget"
- Select a category and enter the budgeted amount
- View budget progress with visual progress bars

### 6. View Dashboard

- The "Dashboard" page shows:
  - Total balance
  - Monthly spending and income
  - Transaction count
  - Spending by category (chart)
  - Recent transactions

## CSV Import Format

Your CSV file should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| date | Yes | Transaction date (YYYY-MM-DD) |
| payee | Yes | Merchant/payee name |
| amount | Yes | Transaction amount (negative for expenses) |
| account_name | No | Account name |
| account_id | No | Account identifier |
| notes | No | Additional notes |
| pending | No | Whether transaction is pending (true/false) |

### Example CSV

```csv
date,payee,amount,account_name
2025-10-01,Starbucks,-5.50,Chase Checking
2025-10-02,Salary,3000.00,Chase Checking
2025-10-03,Amazon,-45.99,Chase Credit Card
2025-10-05,Uber,-15.00,Chase Checking
```

## Default Categories

- Income
- Food & Dining
- Groceries
- Transportation
- Gas & Fuel
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Travel
- Personal Care
- Education
- Gifts & Donations
- Investments
- Transfer
- Other
- Uncategorized

## Performance Optimizations

- **Smart Caching**: Data is cached for 5 minutes to reduce API calls
- **Batch Operations**: Multiple updates are batched into single API calls
- **In-Memory Processing**: All calculations done in pandas, not in Google Sheets
- **Lazy Loading**: Dashboard only loads last 60 days by default

## Security Features

- **Password Hashing**: All passwords hashed with bcrypt
- **Session Management**: Secure session state management
- **Email Validation**: Email format validation on signup
- **Password Strength**: Enforced password complexity requirements

## Google Sheets Schema

The database consists of 7 sheets:

1. **Users** - User accounts
2. **User_Data** - User settings and SimpleFIN URLs
3. **User_Rules** - Categorization rules
4. **Account_Balances** - Account balance snapshots
5. **Budget_Monthly** - Monthly budgets
6. **Recurring_Templates** - Recurring transaction templates
7. **Transactions** - All transactions

## Troubleshooting

### "Failed to open spreadsheet"

- Make sure you've set `SPREADSHEET_ID` in `config.py`
- Verify your service account credentials file exists

### "Failed to authenticate with Google Sheets"

- Check that `my-streamlit-backend-*.json` is in the project directory
- Ensure the service account has access to Google Sheets API

### Slow performance

- Check your internet connection
- Reduce the date range filter on the Transactions page
- Clear cache: Stop the app and restart

### CSV import fails

- Verify your CSV has required columns: `date`, `payee`, `amount`
- Check date format is YYYY-MM-DD
- Ensure amount values are numeric

## Roadmap

### Phase 2: Usability (Week 2)
- Enhanced dashboard layout
- Improved budget visualization
- Bulk categorization features

### Phase 3: Polish (Week 3)
- Charts and trends
- Account balance tracking over time
- Data export functionality

### Phase 4: Optional (Advanced)
- SimpleFIN integration
- AI categorization with Gemini
- Quick insights and recommendations

## Contributing

This is a personal project, but feel free to fork and customize for your own use!

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions, please check the troubleshooting section above or review the code documentation.

---

**Built with ❤️ using Streamlit and Google Sheets**
