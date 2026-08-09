import pytest
from app.engine.document_parser import classify_account, clean_value
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios, calculate_corporate_finance
from app.engine.ai_insights import compute_financial_health_score, generate_ai_insights

def test_account_classification():
    assert classify_account("Cash in Bank") == "CASH_ASSET"
    assert classify_account("Accounts Receivable") == "RECEIVABLE_ASSET"
    assert classify_account("Sales Revenue") == "REVENUE"
    assert classify_account("Office Rent Expense") == "EXPENSE"

def test_clean_value():
    assert clean_value("$1,250.50") == 1250.50
    assert clean_value("(500.00)") == -500.00
    assert clean_value(None) == 0.0

def test_financial_engine_pipeline():
    sample_items = [
        {"account_code": "101", "account_name": "Cash and Bank", "account_type": "CASH_ASSET", "debit": 500000.0, "credit": 0.0, "net_amount": 500000.0, "sheet": "TB"},
        {"account_code": "102", "account_name": "Trade Receivables", "account_type": "RECEIVABLE_ASSET", "debit": 300000.0, "credit": 0.0, "net_amount": 300000.0, "sheet": "TB"},
        {"account_code": "103", "account_name": "Product Inventory", "account_type": "INVENTORY_ASSET", "debit": 200000.0, "credit": 0.0, "net_amount": 200000.0, "sheet": "TB"},
        {"account_code": "201", "account_name": "Trade Payables", "account_type": "PAYABLE_LIABILITY", "debit": 0.0, "credit": 200000.0, "net_amount": -200000.0, "sheet": "TB"},
        {"account_code": "301", "account_name": "Shareholders Equity", "account_type": "EQUITY", "debit": 0.0, "credit": 500000.0, "net_amount": -500000.0, "sheet": "TB"},
        {"account_code": "401", "account_name": "Sales Revenue", "account_type": "REVENUE", "debit": 0.0, "credit": 2000000.0, "net_amount": -2000000.0, "sheet": "TB"},
        {"account_code": "501", "account_name": "Cost of Goods Sold", "account_type": "COGS", "debit": 1000000.0, "credit": 0.0, "net_amount": 1000000.0, "sheet": "TB"},
        {"account_code": "502", "account_name": "Salaries & Rent", "account_type": "EXPENSE", "debit": 400000.0, "credit": 0.0, "net_amount": 400000.0, "sheet": "TB"}
    ]

    statements = generate_financial_statements(sample_items)
    assert statements["income_statement"]["total_revenue"] > 0
    assert statements["income_statement"]["net_income"] > 0
    assert statements["balance_sheet"]["total_assets"] > 0

    ratios = calculate_financial_ratios(statements)
    assert ratios["liquidity"]["current_ratio"]["value"] > 0
    assert ratios["profitability"]["gross_profit_margin"]["value"] > 0

    corp_fin = calculate_corporate_finance(statements, ratios)
    assert "npv" in corp_fin["capital_budgeting"]
    assert "wacc" in corp_fin["capital_structure"]

    health_res = compute_financial_health_score(statements, ratios)
    assert 0 <= health_res["total_score"] <= 100
    assert "profitability" in health_res["sub_scores"]
    assert "liquidity" in health_res["sub_scores"]
    assert "solvency" in health_res["sub_scores"]
    assert "efficiency" in health_res["sub_scores"]

    insights = generate_ai_insights(statements, ratios, corp_fin)
    assert len(insights["recommendations"]) > 0
    assert "health_breakdown" in insights

def test_parse_workbook_formats():
    from app.engine.document_parser import parse_workbook

    # 1. Test CSV format
    csv_bytes = b"account_name,debit,credit\nCash & bank,1000.00,0.00\nAccounts Payable,0.00,500.00"
    res_csv = parse_workbook(csv_bytes, "test.csv")
    assert len(res_csv["normalized_items"]) >= 2
    assert any(i["account_name"] == "Cash & bank" for i in res_csv["normalized_items"])

    # 2. Test JSON format
    json_bytes = b'[{"account_name": "Operating Sales", "net_amount": 25000.0, "account_type": "REVENUE"}]'
    res_json = parse_workbook(json_bytes, "test.json")
    assert len(res_json["normalized_items"]) >= 1
    assert res_json["normalized_items"][0]["account_name"] == "Operating Sales"

    # 3. Test TXT format
    txt_bytes = b"Interest Expense: $1,200.00\nOffice rent: $3,500.00"
    res_txt = parse_workbook(txt_bytes, "test.txt")
    assert len(res_txt["normalized_items"]) >= 2
    assert any("rent" in i["account_name"].lower() for i in res_txt["normalized_items"])

