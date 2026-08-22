"""
Universal Enterprise Golden Benchmark Regression Test Suite
Validates that extraction, statement generation, ratio calculations, and source reconciliation
against universal enterprise source files match expected verified ground-truth figures.

Fails hard if previous synthetic errors (e.g. Revenue=1355.4, Net Profit=-14092.82, Interest=12000) recur.
"""

import pytest
from app.engine.document_parser import parse_workbook
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios
from app.engine.canonical_model import build_canonical_dataset
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.quality_engine import compute_financial_quality_score

def get_mock_enterprise_items():
    """Generates normalized items representing verified enterprise financial statements."""
    return [
        {"account_code": "P&L-1", "account_name": "Revenue from Operations", "account_type": "REVENUE", "net_amount": 92624.0, "source_label": "Revenue from Operations", "sheet": "Profit & Loss", "row": 1, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-2", "account_name": "Other Income", "account_type": "REVENUE", "net_amount": 3899.4, "source_label": "Other Income", "sheet": "Profit & Loss", "row": 2, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-3", "account_name": "Depreciation and Amortization", "account_type": "DEPRECIATION_EXPENSE", "net_amount": 2910.7, "source_label": "Depreciation and Amortization", "sheet": "Profit & Loss", "row": 3, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-4", "account_name": "Finance Costs / Interest Expense", "account_type": "INTEREST_EXPENSE", "net_amount": 1457.7, "source_label": "Finance Costs", "sheet": "Profit & Loss", "row": 4, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-5", "account_name": "Tax Expense", "account_type": "TAX_EXPENSE", "net_amount": 4076.7, "source_label": "Tax Expense", "sheet": "Profit & Loss", "row": 5, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-6", "account_name": "Profit for the Year / Net Income", "account_type": "NET_INCOME", "net_amount": 13197.4, "source_label": "Net Profit", "sheet": "Profit & Loss", "row": 6, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "P&L-7", "account_name": "Operating Expenses", "account_type": "EXPENSE", "net_amount": 70736.1, "source_label": "Operating Expenses", "sheet": "Profit & Loss", "row": 7, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        
        # Balance Sheet
        {"account_code": "BS-1", "account_name": "Cash & Bank Balances", "account_type": "CASH_ASSET", "net_amount": 10555.5, "source_label": "Cash & Bank", "sheet": "Balance Sheet", "row": 10, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-2", "account_name": "Trade Receivables", "account_type": "RECEIVABLE_ASSET", "net_amount": 13590.1, "source_label": "Receivables", "sheet": "Balance Sheet", "row": 11, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-3", "account_name": "Inventories", "account_type": "INVENTORY_ASSET", "net_amount": 51.7, "source_label": "Inventory", "sheet": "Balance Sheet", "row": 12, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-4", "account_name": "Net Property, Plant & Equipment", "account_type": "ASSET", "net_amount": 51690.1, "source_label": "Net Block", "sheet": "Balance Sheet", "row": 13, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-5", "account_name": "Capital Work in Progress", "account_type": "ASSET", "net_amount": 412.2, "source_label": "Capital WIP", "sheet": "Balance Sheet", "row": 14, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-6", "account_name": "Investments", "account_type": "ASSET", "net_amount": 46785.9, "source_label": "Investments", "sheet": "Balance Sheet", "row": 15, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-7", "account_name": "Other Assets", "account_type": "ASSET", "net_amount": 17798.0, "source_label": "Other Assets", "sheet": "Balance Sheet", "row": 16, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        
        {"account_code": "BS-8", "account_name": "Borrowings / Total Debt", "account_type": "DEBT_LIABILITY", "net_amount": 20291.0, "source_label": "Borrowings", "sheet": "Balance Sheet", "row": 20, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-9", "account_name": "Other Liabilities & Payables", "account_type": "LIABILITY", "net_amount": 32574.2, "source_label": "Other Liabilities", "sheet": "Balance Sheet", "row": 21, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        
        {"account_code": "BS-10", "account_name": "Equity Share Capital", "account_type": "EQUITY", "net_amount": 2097.7, "source_label": "Equity Capital", "sheet": "Balance Sheet", "row": 30, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "BS-11", "account_name": "Reserves & Surplus", "account_type": "EQUITY", "net_amount": 85920.6, "source_label": "Reserves", "sheet": "Balance Sheet", "row": 31, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        
        # Cash Flow Statement
        {"account_code": "CF-1", "account_name": "Cash Flow from Operating Activities", "account_type": "CASH_FLOW", "net_amount": 14931.6, "source_label": "Operating Cash Flow", "sheet": "Cash Flow", "row": 40, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "CF-2", "account_name": "Cash Flow from Investing Activities", "account_type": "CASH_FLOW", "net_amount": -2447.5, "source_label": "Investing Cash Flow", "sheet": "Cash Flow", "row": 41, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
        {"account_code": "CF-3", "account_name": "Cash Flow from Financing Activities", "account_type": "CASH_FLOW", "net_amount": -14126.0, "source_label": "Financing Cash Flow", "sheet": "Cash Flow", "row": 42, "column": "B", "year": "2026", "unit": "Millions", "currency": "USD", "is_summary": False},
    ]

def test_enterprise_ground_truth_accuracy_and_reconciliation():
    items = get_mock_enterprise_items()
    statements = generate_financial_statements(items)
    inc = statements["income_statement"]
    bs = statements["balance_sheet"]
    cf = statements["cash_flow"]
    val_rep = statements["validation_report"]

    # 1. Exact Ground-Truth Numeric Assertions
    assert inc["revenue_from_operations"] == 92624.0, f"Expected Revenue 92624.0, got {inc['revenue_from_operations']}"
    assert inc["tax_expense"] == 4076.7, f"Expected Tax 4076.7, got {inc['tax_expense']}"
    assert inc["net_income"] == 13197.4, f"Expected Net Profit 13197.4, got {inc['net_income']}"
    assert inc["interest_expense"] == 1457.7, f"Expected Interest 1457.7, got {inc['interest_expense']}"
    
    assert bs["total_assets"] == 140883.5, f"Expected Assets 140883.5, got {bs['total_assets']}"
    assert bs["total_liabilities"] == 52865.2, f"Expected Liabilities 52865.2, got {bs['total_liabilities']}"
    assert bs["equity"]["total_equity"] == 88018.3, f"Expected Equity 88018.3, got {bs['equity']['total_equity']}"
    
    assert cf["operating_activities"] == 14931.6
    assert cf["investing_activities"] == -2447.5
    assert cf["financing_activities"] == -14126.0
    assert cf["net_change_in_cash"] == -1641.9

    # 2. Accounting Equation Checks
    assert val_rep["balance_sheet_check"] == "PASS"
    assert val_rep["cash_flow_check"] == "PASS"

    # 3. Canonical Model & Reconciliation Engine
    canonical = build_canonical_dataset(items, "Enterprise_Financials.xlsx")
    ratios = calculate_financial_ratios(statements)
    reconciliation = perform_source_to_result_reconciliation(canonical, statements, ratios)
    
    assert reconciliation["reconciliation_status"] == "PASS"
    assert reconciliation["failed_count"] == 0

    # 4. Quality Engine Score
    quality = compute_financial_quality_score(reconciliation, val_rep)
    assert quality["quality_score"] >= 95.0
    assert quality["confidence_level"] == "HIGH"

def test_enterprise_negative_regression_guards():
    """Ensures historical synthetic error figures cause hard test failures."""
    items = get_mock_enterprise_items()
    statements = generate_financial_statements(items)
    inc = statements["income_statement"]

    # Hard regression assertions against past bad outputs
    assert inc["total_revenue"] != 1355.4, "REGRESSION: Revenue was improperly computed as 1355.4"
    assert inc["net_income"] != -14092.82, "REGRESSION: Net profit was improperly computed as -14092.82"
    assert inc["interest_expense"] != 12000.0, "REGRESSION: Interest expense was improperly computed as 12000"
