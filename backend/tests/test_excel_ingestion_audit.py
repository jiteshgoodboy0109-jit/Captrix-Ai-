import pytest
import io
import pandas as pd
from app.engine.document_parser import parse_workbook, clean_value
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios
from app.engine.multi_period_analyzer import generate_multi_period_analysis

def test_company_name_and_multi_year_extraction():
    # Construct a dummy workbook in CSV format
    csv_content = (
        "Entity Name: Acme Corp Ltd.,,\n"
        "Particulars,2023,2024\n"
        "Cash and bank,100.0,200.0\n"
        "Trade Receivables,150.0,250.0\n"
        "Trade Payables,120.0,220.0\n"
        "Share Capital,130.0,230.0\n"
        "Sales Revenue,500.0,700.0\n"
        "Office Rent,300.0,400.0\n"
    )
    
    parsed = parse_workbook(csv_content.encode("utf-8"), "test_file.csv")
    
    assert parsed["company_name"] == "Acme Corp Ltd."
    assert "2023" in parsed["years"]
    assert "2024" in parsed["years"]
    
    items = parsed["normalized_items"]
    # Check that there are items for both years
    years_extracted = set(i["year"] for i in items)
    assert "2023" in years_extracted
    assert "2024" in years_extracted

def test_zero_fabrication_and_non_calculable_ratio():
    # If a line item is missing, check that no multipliers back-model or fabricate it.
    # Here, we don't provide Inventory or Cost of Goods Sold
    items = [
        {"account_code": "1", "account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 100.0, "year": "2024"},
        {"account_code": "2", "account_name": "Accounts Payable", "account_type": "PAYABLE_LIABILITY", "net_amount": -100.0, "year": "2024"},
        {"account_code": "3", "account_name": "Revenue", "account_type": "REVENUE", "net_amount": 200.0, "year": "2024"}
    ]
    
    statements = generate_financial_statements(items)
    
    # Inventory is missing, check it's 0.0, and cost of goods sold is 0.0
    assert statements["balance_sheet"]["current_assets"]["inventory"] == 0.0
    assert statements["income_statement"]["cost_of_goods_sold"] == 0.0
    
    # Denominator check protection: COGS is 0.0, so Inventory Turnover should be non-calculable
    ratios = calculate_financial_ratios(statements)
    inv_turnover = ratios["efficiency"]["inventory_turnover"]
    assert inv_turnover["is_calculable"] is False
    assert "Denominator = 0" in inv_turnover["display_value"]

def test_balance_sheet_equation_audit():
    # Balanced case
    balanced_items = [
        {"account_code": "1", "account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 500.0, "year": "2025"},
        {"account_code": "2", "account_name": "Trade Payables", "account_type": "PAYABLE_LIABILITY", "net_amount": -200.0, "year": "2025"},
        {"account_code": "3", "account_name": "Equity", "account_type": "EQUITY", "net_amount": -300.0, "year": "2025"}
    ]
    
    statements_balanced = generate_financial_statements(balanced_items)
    val_balanced = statements_balanced["validation_report"]
    assert val_balanced["balance_sheet_check"] == "PASS"
    assert val_balanced["is_balanced"] is True
    assert val_balanced["difference"] == 0.0
    
    # Imbalanced case (Assets != Liabilities + Equity)
    imbalanced_items = [
        {"account_code": "1", "account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 500.0, "year": "2025"},
        {"account_code": "2", "account_name": "Trade Payables", "account_type": "PAYABLE_LIABILITY", "net_amount": -200.0, "year": "2025"},
        {"account_code": "3", "account_name": "Equity", "account_type": "EQUITY", "net_amount": -250.0, "year": "2025"}
    ]
    
    statements_imbalanced = generate_financial_statements(imbalanced_items)
    val_imbalanced = statements_imbalanced["validation_report"]
    assert val_imbalanced["balance_sheet_check"] == "FAIL"
    assert val_imbalanced["is_balanced"] is False
    assert val_imbalanced["difference"] == 50.0
