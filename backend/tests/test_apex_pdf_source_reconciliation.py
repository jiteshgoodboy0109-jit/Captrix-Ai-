import io
import pandas as pd
import pytest

from app.engine.document_parser import parse_workbook
from app.engine.canonical_model import build_canonical_dataset
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios

def create_apex_full_source_bytes() -> bytes:
    """Generates Apex Technologies Ltd source Excel bytes containing both multi-year annual & FY2027 quarterly sheets."""
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
            ["Liabilities & Equity", 3, 3, 3, 3],
            ["Cash & Cash Equivalents", 12000, 15000, 18000, 20500],
            ["Accounts Receivable", 14000, 16000, 18500, 20200],
            ["Merchandise Inventory", 6000, 7500, 8400, 9300],
            ["Other Current Assets", 3000, 4000, 4600, 5200],
            ["Property, Plant & Equipment (PPE)", 22000, 25000, 27500, 29600],
            ["Goodwill", 6000, 6000, 6000, 6000],
            ["Intangible Assets", 3000, 4000, 4800, 5400],
            ["Investments", 7000, 8500, 9500, 10500],
            ["Other Non-Current Assets", 2000, 2500, 3000, 3400],
            ["Trade Payables / Accounts Payable", 7000, 8500, 9600, 10500],
            ["Other Current Liabilities", 5000, 6000, 6800, 7600],
            ["Short-Term Borrowings", 1500, 1800, 2100, 2500],
            ["Long-Term Borrowings", 6000, 7200, 8100, 9200],
            ["Other Non-Current Liabilities", 3000, 3800, 4200, 4700],
            ["Share Capital", 10000, 10000, 10000, 10000],
            ["Reserves & Retained Earnings", 40500, 48400, 57400, 65600]
        ]
        pd.DataFrame(bs_data).to_excel(writer, sheet_name="Balance Sheet", header=False, index=False)

        q_data = [
            ["Apex Technologies Ltd. FY2027 Quarterly Statements"],
            ["Particulars", "Q1 FY2027", "Q2 FY2027", "Q3 FY2027", "Q4 FY2027"],
            ["Revenue from Operations", 30500, 31800, 32700, 33900],
            ["Operating Expenses", 9500, 9800, 10200, 10600]
        ]
        pd.DataFrame(q_data).to_excel(writer, sheet_name="Quarters FY2027", header=False, index=False)

    return output.getvalue()

def test_1_annual_pnl_sequence():
    b = create_apex_full_source_bytes()
    parsed = parse_workbook(b, "Apex_Full.xlsx")
    norm_items = parsed["normalized_items"]
    statements = generate_financial_statements(norm_items)
    by_year = statements.get("by_year", {})

    assert by_year["FY2023"]["income_statement"]["revenue_from_operations"] == 78000.0
    assert by_year["FY2024"]["income_statement"]["revenue_from_operations"] == 88000.0
    assert by_year["FY2025"]["income_statement"]["revenue_from_operations"] == 101000.0
    assert by_year["FY2026"]["income_statement"]["revenue_from_operations"] == 116000.0

def test_2_fy2026_income_statement_line_items():
    b = create_apex_full_source_bytes()
    parsed = parse_workbook(b, "Apex_Full.xlsx")
    statements = generate_financial_statements(parsed["normalized_items"])
    fy2026 = statements["by_year"]["FY2026"]["income_statement"]

    assert fy2026["revenue_from_operations"] == 116000.0
    assert fy2026["total_revenue"] == 118800.0
    assert fy2026["cost_of_goods_sold"] == 42920.0
    assert fy2026["gross_profit"] == 73080.0
    assert fy2026["ebitda"] == 36080.0
    assert fy2026["ebit"] == 30380.0
    assert fy2026["ebt"] == 28480.0
    assert fy2026["tax_expense"] == 7120.0
    assert fy2026["net_income"] == 21360.0

def test_3_fy2026_balance_sheet_equation():
    b = create_apex_full_source_bytes()
    parsed = parse_workbook(b, "Apex_Full.xlsx")
    statements = generate_financial_statements(parsed["normalized_items"])
    fy2026_bs = statements["by_year"]["FY2026"]["balance_sheet"]

    assets = fy2026_bs["total_assets"]
    liabilities = fy2026_bs["total_liabilities"]
    equity = fy2026_bs["equity"]["total_equity"]
    status = statements["by_year"]["FY2026"]["validation_report"]["balance_sheet_check"]

    assert assets == 110100.0
    assert liabilities == 34500.0
    assert equity == 75600.0
    assert assets == liabilities + equity
    assert status == "PASS"

def test_4_quarterly_period_isolation():
    b = create_apex_full_source_bytes()
    parsed = parse_workbook(b, "Apex_Full.xlsx")
    statements = generate_financial_statements(parsed["normalized_items"])
    by_year = statements["by_year"]

    # Verify Annual FY2026 Revenue is 116,000 (NOT overwritten by quarterly 30500/31800/32700/33900)
    assert by_year["FY2026"]["income_statement"]["revenue_from_operations"] == 116000.0
    
    # Verify quarterly items are marked as ISOLATED/QUARTERLY
    q_items = [i for i in parsed["normalized_items"] if i.get("is_quarterly")]
    assert len(q_items) > 0, "Quarterly items should be preserved"
    for q in q_items:
        assert q.get("period_type") == "QUARTERLY"

def test_5_pdf_lineage_metadata_preservation():
    b = create_apex_full_source_bytes()
    parsed = parse_workbook(b, "Apex_Full.xlsx")
    for item in parsed["normalized_items"]:
        assert "source_document" in item
        assert "source_table" in item
        assert "source_row" in item
        assert "source_column" in item
        assert "raw_value" in item
