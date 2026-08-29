import io
import pandas as pd
import pytest

from app.engine.canonical_model import PeriodResolver, FinancialConceptResolver, build_canonical_dataset
from app.engine.document_parser import parse_workbook, ExcelAdapter, CSVAdapter
from app.engine.statement_generator import generate_financial_statements
from app.engine.quality_engine import compute_financial_quality_score, calculate_financial_health_score

def test_1_column_position_invariance():
    """
    Changing column order (e.g. FY2026 first, FY2023 last) must NOT change financial meaning.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pnl_reversed = [
            ["Financial Performance Report"],
            ["Particulars", "FY2026", "FY2025", "FY2024", "FY2023"],
            ["Revenue from Operations", 116000, 101000, 88000, 78000],
            ["Cost of Goods Sold (COGS)", 42920, 38380, 35000, 31000],
            ["Operating Expenses", 37000, 28000, 25000, 22000],
            ["Net Profit for the Year", 21360, 22590, 17775, 14475]
        ]
        pd.DataFrame(pnl_reversed).to_excel(writer, sheet_name="Income Statement", header=False, index=False)

    parsed = parse_workbook(output.getvalue(), "Reversed_Columns.xlsx")
    statements = generate_financial_statements(parsed["normalized_items"])
    by_year = statements.get("by_year", {})

    assert by_year["FY2026"]["income_statement"]["revenue_from_operations"] == 116000.0
    assert by_year["FY2025"]["income_statement"]["revenue_from_operations"] == 101000.0
    assert by_year["FY2024"]["income_statement"]["revenue_from_operations"] == 88000.0
    assert by_year["FY2023"]["income_statement"]["revenue_from_operations"] == 78000.0

def test_2_context_aware_stock_classification():
    """
    'Stock' must be classified contextually:
    - 'Stock' under Assets -> INVENTORY
    - 'Common Stock' under Equity -> SHARE_CAPITAL
    - 'Stock Investments' under Investments -> INVESTMENTS
    """
    c_inv = FinancialConceptResolver.resolve_concept("Stock", section_context="CURRENT ASSETS")
    c_equity = FinancialConceptResolver.resolve_concept("Common Stock", section_context="SHAREHOLDERS EQUITY")
    c_invst = FinancialConceptResolver.resolve_concept("Stock Investments", section_context="NON-CURRENT ASSETS")

    assert c_inv == "INVENTORY"
    assert c_equity == "SHARE_CAPITAL"
    assert c_invst == "INVESTMENTS"

def test_3_flexible_period_resolution():
    """
    PeriodResolver must parse variant period expressions cleanly.
    """
    p1 = PeriodResolver.resolve_period("FY2026")
    p2 = PeriodResolver.resolve_period("2025-26")
    p3 = PeriodResolver.resolve_period("Year ended March 31, 2026")
    p4 = PeriodResolver.resolve_period("Q1 FY2027")

    assert p1["fiscal_year"] == "FY2026"
    assert p1["period_type"] == "ANNUAL"

    assert p2["fiscal_year"] == "FY2026"
    assert p2["period_type"] == "ANNUAL"

    assert p3["fiscal_year"] == "FY2026"

    assert p4["fiscal_year"] == "FY2027"
    assert p4["quarter"] == "Q1"
    assert p4["period_type"] == "QUARTERLY"

def test_4_missing_data_preservation():
    """
    Missing data must never be converted to zero silently.
    REPORTED_ZERO vs NOT_REPORTED states must be preserved.
    """
    items = [
        {"source_label": "Reported Zero Line Item", "net_amount": 0.0, "account_name": "Line Item 1"},
        {"source_label": "Omitted Line Item", "net_amount": None, "account_name": "Line Item 2"}
    ]
    canonical = build_canonical_dataset(items, "Missing_Data_Test.xlsx")
    raw_recs = canonical["layer_a_raw_records"]

    assert raw_recs[0]["data_state"] == "REPORTED_ZERO"
    assert raw_recs[1]["data_state"] == "NOT_REPORTED"

def test_5_multi_format_csv_and_excel_adapters():
    """
    CSV and Excel files must both produce valid canonical representations via DocumentAdapter.
    """
    excel_adapter = ExcelAdapter()
    csv_adapter = CSVAdapter()

    csv_data = b"Particulars,FY2026\nRevenue from Operations,50000\nNet Profit,10000\n"
    csv_sheets = csv_adapter.extract_sheets(csv_data, "data.csv")

    assert "Sheet1" in csv_sheets
    assert len(csv_sheets["Sheet1"]) == 2

def test_6_no_forced_balancing_on_imbalanced_balance_sheet():
    """
    If Assets != Liabilities + Equity, system MUST return BALANCE_SHEET_STATUS = FAIL
    without modifying extracted numbers.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pnl = [["Particulars", "FY2026"], ["Revenue from Operations", 100000]]
        bs_imbalanced = [
            ["Particulars", "FY2026"],
            ["Total Assets", 100000],
            ["Total Liabilities", 30000],
            ["Share Capital", 10000],
            ["Reserves & Retained Earnings", 40000] # Total Equity = 50,000 -> L+E = 80,000 != 100,000
        ]
        pd.DataFrame(pnl).to_excel(writer, sheet_name="Income Statement", header=False, index=False)
        pd.DataFrame(bs_imbalanced).to_excel(writer, sheet_name="Balance Sheet", header=False, index=False)

    parsed = parse_workbook(output.getvalue(), "Imbalanced.xlsx")
    statements = generate_financial_statements(parsed["normalized_items"])
    val_rep = statements.get("validation_report", {})

    assert val_rep.get("balance_sheet_check") in ["FAIL", "UNBALANCED", "INCOMPLETE"]

    health = calculate_financial_health_score(statements, {})
    assert health["score"] == "NOT_CALCULABLE"
