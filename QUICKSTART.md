# 🚀 FinDash Quick Start Guide

Get FinDash up and running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

## Step 2: Create Google Sheets Database (2 minutes)

Run the setup script:

```bash
python setup_sheets.py
```

You'll see output like this:

```
Creating spreadsheet: FinDash-DB...
✓ Spreadsheet created: https://docs.google.com/spreadsheets/d/...
✓ Spreadsheet ID: 1a2b3c4d5e6f7g8h9i0j
...
✓ SETUP COMPLETE!
```

**IMPORTANT**: Copy the Spreadsheet ID from the output!

## Step 3: Configure the App (30 seconds)

1. Open `config.py` in your editor
2. Find this line:

```python
SPREADSHEET_ID = ''  # ADD YOUR SPREADSHEET ID HERE
```

3. Paste your Spreadsheet ID:

```python
SPREADSHEET_ID = '1a2b3c4d5e6f7g8h9i0j'  # Your actual ID
```

4. Save the file

## Step 4: Run the App (30 seconds)

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Step 5: Create Your Account (1 minute)

1. Click the **"Sign Up"** tab
2. Fill in:
   - Full Name: `Your Name`
   - Email: `you@example.com`
   - Password: `SecurePass123` (must have 8+ chars, uppercase, lowercase, number)
   - Confirm Password: `SecurePass123`
3. Click **"Sign Up"**
4. Switch to **"Sign In"** tab and log in

## Step 6: Import Sample Data (30 seconds)

1. Click **"Transactions"** in the sidebar
2. Upload the `example_transactions.csv` file
3. Click **"Import Transactions"**

You now have 32 sample transactions with automatic categorization!

## Next Steps

### Explore the Dashboard

Click **"Dashboard"** to see:
- Your total balance
- Monthly spending and income
- Spending by category chart
- Recent transactions

### Categorize Transactions

1. Click **"Categorize"** in the sidebar
2. Review any uncategorized transactions
3. Select the appropriate category
4. Click "Save Category"

### Set Up a Budget

1. Click **"Budgets"** in the sidebar
2. Click "Set Budget"
3. Choose a category (e.g., "Food & Dining")
4. Enter a budget amount (e.g., 500)
5. Click "Save Budget"

### Create Categorization Rules

1. Click **"Rules"** in the sidebar
2. Click "Add New Rule"
3. Example rule:
   - Field: `payee`
   - Condition: `contains`
   - Value: `Starbucks`
   - Category: `Food & Dining`
   - Priority: `1`
4. Click "Add Rule"
5. Click "Apply Rules to All Transactions" to automatically categorize matching transactions

## Common Issues

### "Failed to open spreadsheet"

- Did you add the Spreadsheet ID to `config.py`?
- Check that the ID is inside the quotes

### Can't see the app in browser

- Check the terminal for errors
- Make sure port 8501 isn't in use
- Try navigating manually to `http://localhost:8501`

### Import fails

- Make sure your CSV has columns: `date`, `payee`, `amount`
- Check that dates are in YYYY-MM-DD format
- Ensure amounts are numbers (negative for expenses)

## Tips for Best Experience

### Mobile Use

- The app is mobile-friendly!
- Open `http://your-computer-ip:8501` on your phone (same network)

### CSV Format

Your bank's CSV export should work with minimal changes:
- Rename columns to: `date`, `payee`, `amount`
- Format dates as YYYY-MM-DD
- Make expenses negative (e.g., -50.00)

### Performance

- The app caches data for 5 minutes
- Default view shows last 60 days of transactions
- Use date filters to narrow down large datasets

## What's Next?

Now that you're set up, you can:

1. **Import your real bank data** - Export CSV from your bank and import
2. **Set monthly budgets** - Track spending against budgets
3. **Create rules** - Automate categorization for recurring merchants
4. **Explore analytics** - View spending trends and patterns

For more detailed information, see the full [README.md](README.md)

---

**Need help?** Check the troubleshooting section in README.md
