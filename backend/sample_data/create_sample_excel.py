import os
import pandas as pd

def generate_sample_workbook():
    os.makedirs("sample_data", exist_ok=True)
    file_path = os.path.join("sample_data", "Acme_Corp_Financials_2025.xlsx")

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        # Sheet 1: Trial Balance
        tb_data = [
            {"Account Code": "1010", "Particulars": "Cash and Cash Equivalents", "Debit": 450000.0, "Credit": 0.0, "Type": "ASSET"},
            {"Account Code": "1020", "Particulars": "Accounts Receivable", "Debit": 320000.0, "Credit": 0.0, "Type": "ASSET"},
            {"Account Code": "1030", "Particulars": "Merchandise Inventory", "Debit": 280000.0, "Credit": 0.0, "Type": "ASSET"},
            {"Account Code": "1510", "Particulars": "Property, Plant & Equipment", "Debit": 1250000.0, "Credit": 0.0, "Type": "ASSET"},
            {"Account Code": "2010", "Particulars": "Accounts Payable", "Debit": 0.0, "Credit": 210000.0, "Type": "LIABILITY"},
            {"Account Code": "2020", "Particulars": "Short Term Commercial Loan", "Debit": 0.0, "Credit": 150000.0, "Type": "LIABILITY"},
            {"Account Code": "2510", "Particulars": "Long Term Corporate Bond", "Debit": 0.0, "Credit": 600000.0, "Type": "LIABILITY"},
            {"Account Code": "3010", "Particulars": "Common Share Capital", "Debit": 0.0, "Credit": 500000.0, "Type": "EQUITY"},
            {"Account Code": "3020", "Particulars": "Retained Earnings", "Debit": 0.0, "Credit": 840000.0, "Type": "EQUITY"},
            {"Account Code": "4010", "Particulars": "Gross Product Sales Revenue", "Debit": 0.0, "Credit": 2400000.0, "Type": "REVENUE"},
            {"Account Code": "4020", "Particulars": "Software Subscriptions Revenue", "Debit": 0.0, "Credit": 650000.0, "Type": "REVENUE"},
            {"Account Code": "5010", "Particulars": "Cost of Goods Sold (COGS)", "Debit": 1280000.0, "Credit": 0.0, "Type": "EXPENSE"},
            {"Account Code": "5020", "Particulars": "Salaries and Wages Expense", "Debit": 520000.0, "Credit": 0.0, "Type": "EXPENSE"},
            {"Account Code": "5030", "Particulars": "Facility Rent & Utilities", "Debit": 110000.0, "Credit": 0.0, "Type": "EXPENSE"},
            {"Account Code": "5040", "Particulars": "Marketing & Ad Spend", "Debit": 85000.0, "Credit": 0.0, "Type": "EXPENSE"},
            {"Account Code": "5050", "Particulars": "Depreciation Expense", "Debit": 65000.0, "Credit": 0.0, "Type": "EXPENSE"}
        ]
        pd.DataFrame(tb_data).to_excel(writer, sheet_name="Trial Balance", index=False)

        # Sheet 2: Journal Entries
        journal_data = [
            {"Voucher No": "V-101", "Date": "2025-01-15", "Account Name": "Gross Product Sales Revenue", "Debit": 0.0, "Credit": 200000.0},
            {"Voucher No": "V-102", "Date": "2025-01-18", "Account Name": "Salaries and Wages Expense", "Debit": 45000.0, "Credit": 0.0},
            {"Voucher No": "V-103", "Date": "2025-01-25", "Account Name": "Facility Rent & Utilities", "Debit": 12000.0, "Credit": 0.0}
        ]
        pd.DataFrame(journal_data).to_excel(writer, sheet_name="Journal", index=False)

        # Sheet 3: Ledger Summary
        ledger_data = [
            {"Account Code": "1010", "Account Name": "Cash and Cash Equivalents", "Category": "ASSET", "Net Amount": 450000.0},
            {"Account Code": "2010", "Account Name": "Accounts Payable", "Category": "LIABILITY", "Net Amount": -210000.0},
            {"Account Code": "4010", "Account Name": "Gross Product Sales Revenue", "Category": "REVENUE", "Net Amount": -2400000.0}
        ]
        pd.DataFrame(ledger_data).to_excel(writer, sheet_name="Ledger", index=False)

    print(f"Sample workbook generated cleanly at: {file_path}")

if __name__ == "__main__":
    generate_sample_workbook()
