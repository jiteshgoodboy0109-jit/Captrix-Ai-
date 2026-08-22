"""
Comprehensive Financial Pipeline Acceptance Test Suite.
Verifies all 11 mandatory financial engine requirements using the Apex Technologies Ltd dataset.
"""

import io
import pytest
import pandas as pd
from app.engine.document_parser import (
    parse_workbook,
    classify_account,
    detect_year_columns,
    is_non_financial_header
)
from app.engine.canonical_model import build_canonical_dataset
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios
from app.engine.quality_engine import calculate_financial_health_score
from app.reports.excel_generator import generate_excel_report


def build_apex_test_workbook_bytes() -> bytes:
    """Generates Apex Technologies Ltd test Excel workbook in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pnl_data = [
            ["Apex Technologies Ltd. Financial Statements"],
            ["Particulars", "FY2023", "FY2024", "FY2025", "FY2026"],
            ["Revenue from Operations", 78000, 88000, 101000, 116000],
            ["Other Income", 1500, 2000, 2400, 2800],
            ["Cost of Goods Sold (COGS)", 31000, 35000, 38380, 42920],
            ["Operating Expenses", 22000, 25000, 28000, 37000],
            ["Depreciation & Amortization", 4000, 4800, 5200, 5700],
            ["Finance Costs / Interest Expense", 1200, 1500, 1700, 1900],
            ["Profit Before Tax (PBT)", 19300, 23700, 30120, 28480],
            ["Tax Expense", 4825, 5925, 7530, 7120],
            ["Net Profit for the Year", 14475, 17775, 22590, 21360]
        ]
        pd.DataFrame(pnl_data).to_excel(writer, sheet_name="Income Statement", header=False, index=False)

        bs_data = [
            ["Apex Technologies Ltd. Balance Sheet"],
            ["Particulars", "FY2023", "FY2024", "FY2025", "FY2026"],
            ["Cash & Cash Equivalents", 12000, 15000, 18000, 20500],
            ["Accounts Receivable", 14000, 16000, 18500, 20200],
            ["Merchandise Inventory", 6000, 7500, 8400, 9300],
            ["Other Current Assets", 3000, 4000, 4600, 5200],
            ["Property, Plant & Equipment (PPE)", 22000, 25000, 27500, 29600],
            ["Goodwill", 6000, 6000, 6000, 6000],
            ["Intangible Assets", 3000, 4000, 4800, 5400],
            ["Investments", 7000, 8500, 9500, 10500],
            ["Other Non-Current Assets", 2000, 2500, 3000, 3400],
            ["Trade Payables", 7000, 8500, 9600, 10500],
            ["Other Current Liabilities", 5000, 6000, 6800, 7600],
            ["Short-Term Borrowings", 1500, 1800, 2100, 2500],
            ["Long-Term Borrowings", 6000, 7200, 8100, 9200],
            ["Other Non-Current Liabilities", 3000, 3800, 4200, 4700],
            ["Share Capital", 10000, 10000, 10000, 10000],
            ["Reserves & Retained Earnings", 40500, 48400, 57400, 65600]
        ]
        pd.DataFrame(bs_data).to_excel(writer, sheet_name="Balance Sheet", header=False, index=False)

    return output.getvalue()


# 1. Fiscal Year Mapping Test
def test_fiscal_year_mapping():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    norm_items = parsed.get("normalized_items", [])
    assert len(norm_items) > 0, "Failed to extract normalized line items"
    
    sample = norm_items[0]
    assert "period_raw" in sample, "Missing period_raw field"
    assert "fiscal_year" in sample, "Missing fiscal_year field"
    assert "period_type" in sample, "Missing period_type field"
    assert "source_sheet" in sample, "Missing source_sheet field"
    assert "source_cell" in sample, "Missing source_cell field"
    assert "source_column" in sample, "Missing source_column field"
    assert sample.get("is_valid") is True, "Source cell record must be valid"


# 2. Revenue Extraction Test
def test_revenue_extraction():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    inc = stmts.get("income_statement", {})

    assert inc.get("sales") == 116000, f"Expected Revenue from Operations = 116000, got {inc.get('sales')}"
    assert inc.get("other_income") == 2800, f"Expected Other Income = 2800, got {inc.get('other_income')}"
    assert inc.get("total_revenue") == 118800, f"Expected Total Revenue = 118800, got {inc.get('total_revenue')}"


# 3. Equity Classification Test
def test_equity_classification():
    assert classify_account("Common Stock") == "EQUITY"
    assert classify_account("Share Capital") == "EQUITY"
    assert classify_account("Equity Share Capital") == "EQUITY"
    assert classify_account("Retained Earnings") == "EQUITY"
    assert classify_account("Reserves & Surplus") == "EQUITY"
    assert classify_account("Merchandise Inventory") == "INVENTORY_ASSET"


# 4. Liability Classification Test
def test_liability_classification():
    assert classify_account("Trade Payables") == "PAYABLE_LIABILITY"
    assert classify_account("Other Current Liabilities") in ["LIABILITY", "PAYABLE_LIABILITY"]
    assert classify_account("Short-Term Borrowings") == "DEBT_LIABILITY"
    assert classify_account("Long-Term Borrowings") == "DEBT_LIABILITY"


# 5. P&L Reconciliation Test
def test_pnl_reconciliation():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    inc = stmts.get("income_statement", {})

    assert inc.get("gross_profit") == 73080, f"Gross Profit expected 73080, got {inc.get('gross_profit')}"
    assert inc.get("ebitda") == 36080, f"EBITDA expected 36080, got {inc.get('ebitda')}"
    assert inc.get("ebit") == 30380, f"EBIT expected 30380, got {inc.get('ebit')}"
    assert inc.get("ebt") == 28480, f"PBT expected 28480, got {inc.get('ebt')}"
    assert inc.get("tax_expense") == 7120, f"Tax Expense expected 7120, got {inc.get('tax_expense')}"
    assert inc.get("net_income") == 21360, f"Net Profit expected 21360, got {inc.get('net_income')}"


# 6. Balance Sheet Reconciliation Test
def test_balance_sheet_reconciliation():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    bs = stmts.get("balance_sheet", {})
    val_rep = stmts.get("validation_report", {})

    total_assets = bs.get("total_assets")
    total_liabs = bs.get("total_liabilities")
    total_eq = bs.get("equity", {}).get("total_equity")

    assert total_assets == 110100, f"Expected Total Assets = 110100, got {total_assets}"
    assert total_liabs == 34500, f"Expected Total Liabilities = 34500, got {total_liabs}"
    assert total_eq == 75600, f"Expected Total Equity = 75600, got {total_eq}"
    assert total_assets == total_liabs + total_eq, f"Balance sheet equation failed: {total_assets} != {total_liabs} + {total_eq}"
    assert val_rep.get("balance_sheet_check") == "PASS"


# 7. Missing Value Handling Test
def test_missing_value_handling():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    inc = stmts.get("income_statement", {})
    
    assert inc.get("cogs_status") in ["VERIFIED", "NOT_REPORTED"]


# 8. Trial Balance Applicability Test
def test_trial_balance_applicability():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    tb = stmts.get("trial_balance", {})

    assert tb.get("status") == "NOT_APPLICABLE", f"Trial balance expected NOT_APPLICABLE, got {tb.get('status')}"


# 9. Ratio Validation Test
def test_ratio_validation():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    ratios = calculate_financial_ratios(stmts)

    prof = ratios.get("profitability", {})
    liq = ratios.get("liquidity", {})
    solv = ratios.get("solvency", {})

    gp_margin = prof.get("gross_profit_margin", {}).get("value")
    np_margin = prof.get("net_profit_margin", {}).get("value")
    cr = liq.get("current_ratio", {}).get("value")
    de = solv.get("debt_to_equity", {}).get("value")
    dr = solv.get("debt_ratio", {}).get("value")
    eq_r = solv.get("equity_ratio", {}).get("value")
    ic = solv.get("interest_coverage_ratio", {}).get("value") or solv.get("interest_coverage", {}).get("value")

    assert abs(gp_margin - 61.52) < 0.2, f"Gross Margin expected ~61.52%, got {gp_margin}"
    assert abs(np_margin - 17.98) < 0.2, f"Net Margin expected ~17.98%, got {np_margin}"
    assert abs(cr - 2.68) < 0.1, f"Current Ratio expected ~2.68, got {cr}"
    assert abs(de - 0.15) < 0.1, f"Debt-to-Equity expected ~0.15, got {de}"
    assert abs(dr - 31.33) < 0.2, f"Debt Ratio expected ~31.33%, got {dr}"
    assert abs(eq_r - 68.67) < 0.2, f"Equity Ratio expected ~68.67%, got {eq_r}"
    assert abs(ic - 15.99) < 0.2, f"Interest Coverage expected ~15.99x, got {ic}"


# 10. ROCE Safety Test
def test_roce_safety():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    ratios = calculate_financial_ratios(stmts)
    roce = ratios.get("profitability", {}).get("return_on_capital_employed", {})

    roce_val = roce.get("value")
    if roce_val is not None:
        assert roce_val != 823900, f"ROCE must NOT be 823900%, got {roce_val}"
        assert -100.0 <= float(roce_val) <= 100.0, f"ROCE out of safe bounds [-100%, +100%]: {roce_val}"
    else:
        assert roce.get("display_value") in ["NOT_CALCULABLE", "Ratio Not Calculable — Required Source Data Missing / Denominator = 0"]


# 11. Excel Output Validation Test
def test_excel_output_validation():
    file_bytes = build_apex_test_workbook_bytes()
    parsed = parse_workbook(file_bytes, "Apex_Financials.xlsx")
    stmts = generate_financial_statements(parsed.get("normalized_items", []))
    ratios = calculate_financial_ratios(stmts)
    
    excel_bytes = generate_excel_report("Apex Technologies Ltd.", stmts, ratios, {}, {"executive_summary": "Test summary", "recommendations": []})
    assert len(excel_bytes) > 0, "Excel output byte stream is empty"

    xls = pd.ExcelFile(io.BytesIO(excel_bytes))
    sheet_names = xls.sheet_names

    assert "Executive Summary & Health" in sheet_names, "Missing Executive Summary sheet"
    assert "Source Data Summary" in sheet_names, "Missing Source Data Summary sheet"
    assert "Statements (Multi-Year)" in sheet_names, "Missing Multi-Year Statements sheet"
    assert "Validation & Audit Report" in sheet_names, "Missing Validation sheet"
