import sqlite3
import json

def inspect_database():
    conn = sqlite3.connect("financial_platform.db")
    cursor = conn.cursor()

    print("==================================================")
    print("       AI FINANCIAL PLATFORM DATABASE DUMP        ")
    print("==================================================")

    # 1. Registered Users
    print("\n--- USERS TABLE ---")
    cursor.execute("SELECT id, email, full_name, role, created_at FROM users")
    users = cursor.fetchall()
    if not users:
        print("No users found.")
    for u in users:
        print(f"ID #{u[0]} | Email: {u[1]} | Name: {u[2]} | Role: {u[3]} | Created: {u[4]}")

    # 2. Uploaded Workbooks
    print("\n--- UPLOADS TABLE ---")
    cursor.execute("SELECT id, user_id, filename, file_size, sheet_names, status, created_at FROM uploads")
    uploads = cursor.fetchall()
    if not uploads:
        print("No uploads found.")
    for up in uploads:
        sheets = json.loads(up[4]) if up[4] else []
        print(f"Upload #{up[0]} | User ID #{up[1]} | File: {up[2]} ({up[3]} bytes) | Sheets: {sheets} | Status: {up[5]}")

    # 3. Analysis History Log
    print("\n--- ANALYSIS HISTORY TABLE ---")
    cursor.execute("SELECT id, upload_id, company_name, health_score, report_name, timestamp FROM history")
    history = cursor.fetchall()
    if not history:
        print("No history records found.")
    for h in history:
        print(f"History #{h[0]} | Upload #{h[1]} | Company: {h[2]} | Health Score: {h[3]}/100 | Report: {h[4]} | Time: {h[5]}")

    # 4. Financial Statements Summary
    print("\n--- FINANCIAL STATEMENTS TABLE ---")
    cursor.execute("SELECT id, upload_id, balance_sheet, income_statement FROM statements")
    stmts = cursor.fetchall()
    for s in stmts:
        bs = json.loads(s[2])
        inc = json.loads(s[3])
        total_assets = bs.get('total_assets', 0)
        net_income = inc.get('net_income', 0)
        print(f"Statement Record #{s[0]} (Upload #{s[1]}): Total Assets: ${total_assets:,.2f} | Net Income: ${net_income:,.2f}")

    conn.close()

if __name__ == "__main__":
    inspect_database()
