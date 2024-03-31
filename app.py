import streamlit as st
import sqlite3
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import hashlib
import docx
import csv
import xlrd

# Initialize SQLite database
conn = sqlite3.connect('finance_assistant.db')
c = conn.cursor()

# Create tables for user data, spending, and transactions
c.execute('''CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY_KEY,
            user_name TEXT,
            encrypted_password TEXT,
            bank_account_number TEXT,
            bank_token TEXT)''')

# Drop the transactions table if it exists
c.execute('''DROP TABLE IF EXISTS transactions''')

# Create the transactions table with the amount column
c.execute('''CREATE TABLE transactions (
            id INTEGER PRIMARY_KEY,
            user_name TEXT,
            transaction_text TEXT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL)''')

# Function to add user data
def add_user_data():
    st.write("### Add User Data")
    user_name = st.text_input("Enter User Name", key="user_name_add")
    password = st.text_input("Enter Password", type="password", key="password_add")
    bank_account_number = st.text_input("Enter Bank Account Number", key="bank_account_number_add")
    bank_token = st.text_input("Enter Bank Token", key="bank_token_add")
    if st.button("Submit"):
        # Encrypt password before storing        
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO user_data (user_name, encrypted_password, bank_account_number, bank_token) VALUES (?, ?, ?, ?)", (user_name, encrypted_password, bank_account_number, bank_token))
        conn.commit()
        st.write("User data added successfully!")

# Function to upload bank statements
def upload_bank_statements():
    st.write("### Upload Bank Statements")
    user_name = st.text_input("Enter User Name", key="user_name_upload")
    file = st.file_uploader("Choose a file", type=["pdf"])
    if file is not None:
        try:
            pdf = PdfReader(BytesIO(file.getvalue()))
            transactions = []
            for page in pdf.pages:
                transactions.extend(page.extract_text().split('\n'))  # Split by lines instead of words
            for transaction in transactions:
                # TODO: Extract date, description, category, and amount from transaction
                date = '2021-01-01'  # Replace with actual date
                description = 'Some description'  # Replace with actual description
                category = 'Some category'  # Replace with actual category
                amount = 100.0  # Replace with actual amount
                # Store transaction data in SQLite database
                c.execute("INSERT INTO transactions (user_name, transaction_text, date, description, category, amount) VALUES (?, ?, ?, ?, ?, ?)", (user_name, transaction, date, description, category, amount))
            conn.commit()
            st.write("Bank statements uploaded successfully!")
            generate_report(user_name)
        except Exception as e:
            st.write("An error occurred while processing the PDF file. Please make sure the file is in the correct format.")
            print(e)

# Function to upload company statements
def upload_company_statements():
    st.write("### Upload Company Statements")
    company_name = st.text_input("Enter Company Name", key="company_name_upload")
    file = st.file_uploader("Choose a file", type=["pdf"], key="company_file_uploader")
    if file is not None:
        try:
            pdf = PdfReader(BytesIO(file.getvalue()))
            transactions = []
            for page in pdf.pages:
                transactions.extend(page.extract_text().split('\n'))  # Split by lines instead of words
            for transaction in transactions:
                # TODO: Extract date, description, category, and amount from transaction
                date = '2021-01-01'  # Replace with actual date
                description = 'Some description'  # Replace with actual description
                category = 'Some category'  # Replace with actual category
                amount = 100.0  # Replace with actual amount
                # Store transaction data in SQLite database
                c.execute("INSERT INTO transactions (user_name, transaction_text, date, description, category, amount) VALUES (?, ?, ?, ?, ?, ?)", (company_name, transaction, date, description, category, amount))
            conn.commit()
            st.write("Company statements uploaded successfully!")
            generate_report(company_name)
        except Exception as e:
            st.write("An error occurred while processing the PDF file. Please make sure the file is in the correct format.")
            print(e)

# Function to upload company financial documents
def upload_company_financial_documents():
    st.write("### Upload Company Financial Documents")
    company_name = st.text_input("Enter Company Name", key="company_name_upload_financial")
    file = st.file_uploader("Choose a file", type=["pdf", "txt", "doc", "docx", "xls", "xlsx", "csv"], key="company_file_uploader_financial")
    if file is not None:
        try:
            if file.type == "application/pdf":
                pdf = PdfReader(BytesIO(file.getvalue()))
                transactions = []
                for page in pdf.pages:
                    transactions.extend(page.extract_text().split('\n'))  # Split by lines instead of words
            elif file.type == "text/plain":
                transactions = file.getvalue().decode().split('\n')
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(BytesIO(file.getvalue()))
                transactions = [p.text for p in doc.paragraphs]
            elif file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                workbook = xlrd.open_workbook(file_contents=file.getvalue())
                sheet = workbook.sheet_by_index(0)
                transactions = [sheet.row_values(i) for i in range(sheet.nrows)]
            elif file.type == "text/csv":
                reader = csv.reader(BytesIO(file.getvalue()).decode().splitlines())
                transactions = list(reader)
            for transaction in transactions:
                # TODO: Extract date, description, category, and amount from transaction
                date = '2021-01-01'  # Replace with actual date
                description = 'Some description'  # Replace with actual description
                category = 'Some category'  # Replace with actual category
                amount = 100.0  # Replace with actual amount
                # Store transaction data in SQLite database
                c.execute("INSERT INTO transactions (user_name, transaction_text, date, description, category, amount) VALUES (?, ?, ?, ?, ?, ?)", (company_name, transaction, date, description, category, amount))
            conn.commit()
            st.write("Company financial documents uploaded successfully!")
            generate_report(company_name)
        except Exception as e:
            st.write("Good job! You are saving money. Keep it up.")
            print(e)

# Function to generate report
def generate_report(user_name):
    st.write("### Report")
    # Calculate total spending by category
    c.execute("SELECT category, SUM(amount) FROM transactions WHERE user_name = ? GROUP BY category", (user_name,))
    spending_by_category = pd.DataFrame(c.fetchall(), columns=['Category', 'Total'])
    st.write("Spending by category:")
    st.bar_chart(spending_by_category)
    # Find most and least spent categories
    most_spent_category = spending_by_category.loc[spending_by_category['Total'].idxmax()]['Category']
    least_spent_category = spending_by_category.loc[spending_by_category['Total'].idxmin()]['Category']
    st.write(f"Most spent category: {most_spent_category}")
    st.write(f"Least spent category: {least_spent_category}")
    # Calculate spending over time
    c.execute("SELECT date, SUM(amount) FROM transactions WHERE user_name = ? GROUP BY date", (user_name,))
    spending_over_time = pd.DataFrame(c.fetchall(), columns=['Date', 'Total'])
    st.write("Spending over time:")
    st.line_chart(spending_over_time)
    # Calculate average spending per day
    average_spending_per_day = spending_over_time['Total'].mean()
    st.write(f"Average spending per day: {average_spending_per_day}")
    # Calculate spending trend
    spending_trend = (spending_over_time['Total'].iloc[-1] - spending_over_time['Total'].iloc[0]) / spending_over_time['Total'].iloc[0]
    st.write(f"Spending trend: {'Increasing' if spending_trend > 0 else 'Decreasing'} by {abs(spending_trend * 100)}%")
    # Calculate total income and total spending
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_name = ? AND amount > 0", (user_name,))
    total_income = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_name = ? AND amount < 0", (user_name,))
    total_spending = c.fetchone()[0]
    st.write(f"Total income: {total_income}")
    st.write(f"Total spending: {total_spending}")
    # Calculate savings
    savings = total_income + total_spending  # Spending is negative
    st.write(f"Savings: {savings}")
    # Suggest savings if spending is more than income
    if savings < 0:
        st.write("You are spending more than your income. Try to cut down on your expenses to increase your savings.")
    else:
        st.write("Good job! You are saving money. Keep it up!")

# Add user data feature
add_user_data()

# Upload bank statements feature
upload_bank_statements()

# Upload company statements feature
upload_company_statements()

# Upload company financial documents feature
upload_company_financial_documents()

# Close the database connection
conn.close()