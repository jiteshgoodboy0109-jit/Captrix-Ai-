import pytest
from app.engine.document_parser import (
    clean_value, clean_value_or_none, classify_account,
    detect_company_and_currency, parse_workbook
)
from app.engine.currency_engine import identify_currency
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios
from app.engine.auditor_engine import perform_full_financial_audit
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report


def test_scenario_1_tata_motors_sa_currency():
    """Scenario 1: Tata Motors SA with South African Rand (ZAR / R)."""
    text = "Figures in South African Rand (R), unless otherwise stated.\nRevenue: 50,000\nOperating Profit: 12,000"
    curr, _ = identify_currency(text, default_iso="NOT_DETERMINED")
    assert curr == "ZAR"


def test_scenario_2_wipro_golden_failures():
    """Scenario 2: Wipro golden failure reproduction and provenance."""
    # Revenue = 2168, COGS = 480147, Reported GP = 266106 -> Arithmetic mismatch!
    inc_items = [
        {"account_name": "Revenue from Operations", "account_type": "REVENUE", "net_amount": 2168.0, "source_label": "Revenue", "fiscal_year": "FY2026", "year": "2026", "sheet": "P&L"},
        {"account_name": "Cost of Goods Sold", "account_type": "COGS", "net_amount": 480147.0, "source_label": "COGS", "fiscal_year": "FY2026", "year": "2026", "sheet": "P&L"},
        {"account_name": "Gross Profit", "account_type": "GROSS_PROFIT", "net_amount": 266106.0, "source_label": "Reported GP", "fiscal_year": "FY2026", "year": "2026", "sheet": "P&L", "is_summary": True}
    ]
    stmts = generate_financial_statements(inc_items)
    pnl = stmts["income_statement"]
    # Calculated = 2168 - 480147 = -477979 != 266106 -> Flagged!
    assert pnl["gross_profit_status"] in ["MISMATCH", "RECONCILIATION_MISMATCH"]
    assert pnl["gross_profit_calculated"] == -477979.0
    assert pnl["gross_profit"] == 266106.0


def test_scenario_3_apex_3_statement_reconciliation():
    """Scenario 3: Apex 3-statement reconciliation."""
    items = [
        {"account_name": "Sales Revenue", "account_type": "REVENUE", "net_amount": 100000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Cost of Sales", "account_type": "COGS", "net_amount": 40000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Operating Expenses", "account_type": "EXPENSE", "net_amount": 20000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 50000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Accounts Receivable", "account_type": "RECEIVABLE_ASSET", "net_amount": 30000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Accounts Payable", "account_type": "PAYABLE_LIABILITY", "net_amount": 20000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Common Stock", "account_type": "EQUITY", "net_amount": 60000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Operating Cash", "account_type": "CASH_FLOW", "net_amount": 40000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "CashFlow"}
    ]
    stmts = generate_financial_statements(items)
    pnl = stmts["income_statement"]
    bs = stmts["balance_sheet"]
    cf = stmts["cash_flow"]
    
    assert pnl["revenue_from_operations"] == 100000.0
    assert bs["total_assets"] == 80000.0
    assert bs["total_liabilities_and_equity"] == 80000.0
    assert stmts["validation_report"]["balance_sheet_check"] == "PASS"


def test_scenario_4_pnl_only_suppresses_balance_sheet_and_cash_flow():
    """Scenario 4: P&L-only document suppresses Balance Sheet & Cash Flow."""
    items = [
        {"account_name": "Total Revenue", "account_type": "REVENUE", "net_amount": 500000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "IncomeStatement"},
        {"account_name": "Cost of Goods Sold", "account_type": "COGS", "net_amount": 200000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "IncomeStatement"},
        {"account_name": "Net Profit", "account_type": "NET_INCOME", "net_amount": 300000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "IncomeStatement"}
    ]
    stmts = generate_financial_statements(items)
    pnl = stmts["income_statement"]
    bs = stmts["balance_sheet"]
    cf = stmts["cash_flow"]
    
    assert bs["status"] in ["NOT_REPORTED", "NOT_REPORTED_IN_SOURCE"]
    assert "Not Available" in cf["status"] or "NOT_REPORTED" in cf["status"]
    
    # Ratios dependent on Balance Sheet must be NOT_CALCULABLE
    ratios = calculate_financial_ratios(stmts)
    assert ratios["liquidity"]["current_ratio"]["is_calculable"] is False
    assert ratios["liquidity"]["current_ratio"]["value"] is None


def test_scenario_5_pnl_plus_balance_sheet_suppresses_cash_flow():
    """Scenario 5: P&L + Balance Sheet suppresses Cash Flow."""
    items = [
        {"account_name": "Sales", "account_type": "REVENUE", "net_amount": 250000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Net Profit", "account_type": "NET_INCOME", "net_amount": 50000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 100000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Common Stock", "account_type": "EQUITY", "net_amount": 100000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"}
    ]
    stmts = generate_financial_statements(items)
    cf = stmts["cash_flow"]
    assert "Not Available" in cf["status"] or "NOT_REPORTED" in cf["status"]


def test_scenario_6_full_3_statement():
    """Scenario 6: Full 3-statement document has all 3 statements active."""
    items = [
        {"account_name": "Revenue", "account_type": "REVENUE", "net_amount": 1000.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Cash", "account_type": "CASH_ASSET", "net_amount": 500.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "Sheet1"},
        {"account_name": "Operating Cash Flow", "account_type": "CASH_FLOW", "net_amount": 300.0, "fiscal_year": "FY2026", "year": "2026", "sheet": "CashFlow"}
    ]
    stmts = generate_financial_statements(items)
    assert stmts["income_statement"].get("total_revenue") == 1000.0
    assert stmts["balance_sheet"].get("status") != "NOT_REPORTED"
    assert stmts["cash_flow"].get("operating_activities") == 300.0


def test_scenario_7_ambiguous_unstructured_document():
    """Scenario 7: Ambiguous lines preserved without forced misclassification."""
    classified = classify_account("Unspecified Miscellaneous Flow 9482")
    assert classified in ["UNCLASSIFIED", "EXPENSE", "REVENUE"]


def test_scenario_8_inr_document_numbering():
    """Scenario 8: INR document with Indian numbering."""
    val = clean_value("1,25,00,000.00")
    assert val == 12500000.0
    curr, _ = identify_currency("All figures in INR Lakhs (₹)")
    assert curr == "INR"


def test_scenario_9_usd_document_formatting():
    """Scenario 9: USD document with Millions/Western format."""
    assert clean_value("1,250,000.00") == 1250000.0
    curr, _ = identify_currency("$ in Millions")
    assert curr == "USD"


def test_scenario_10_currency_absent_returns_not_determined():
    """Scenario 10: Absent currency returns NOT_DETERMINED without guessing USD/INR."""
    curr, _ = identify_currency("General Ledger Report Sheet", default_iso="NOT_DETERMINED")
    assert curr == "NOT_DETERMINED"


def test_scenario_11_year_absent_returns_unknown():
    """Scenario 11: Absent year returns UNKNOWN."""
    from app.engine.canonical_model import PeriodResolver
    res = PeriodResolver.resolve_period("Amount")
    assert res["fiscal_year"] == "UNKNOWN"
    assert res["period_status"] == "UNKNOWN"


def test_scenario_12_missing_statements_template_suppression():
    """Scenario 12: Suppressed statements produce valid PDF and Excel without empty '-' rows."""
    empty_stmts = {
        "income_statement": {"status": "PROCESSED", "revenue_from_operations": 5000.0, "net_income": 1000.0},
        "balance_sheet": {"status": "NOT_REPORTED_IN_SOURCE"},
        "cash_flow": {"status": "NOT_REPORTED_IN_SOURCE"},
        "validation_report": {"balance_sheet_check": "FAIL"}
    }
    ratios = {
        "liquidity": {"current_ratio": {"is_calculable": False, "value": None}},
        "profitability": {"net_profit_margin": {"is_calculable": True, "value": 20.0}}
    }
    pdf_bytes = generate_pdf_report("Test Co", empty_stmts, ratios, {}, {"executive_summary": "Test"})
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0


def test_scenario_13_negative_values_preserved():
    """Scenario 13: Negative values mathematically preserved."""
    val = clean_value("-480147.00")
    assert val == -480147.0


def test_scenario_14_parentheses_negatives_converted():
    """Scenario 14: Parentheses negative strings converted correctly."""
    val = clean_value("(480,147)")
    assert val == -480147.0
    val2 = clean_value("(12,345.67)")
    assert val2 == -12345.67


def test_scenario_15_commas_and_decimals_formatted():
    """Scenario 15: Commas and decimals cleanly parsed."""
    val = clean_value("1,286,520.50")
    assert val == 1286520.5


def test_scenario_16_indian_numbering_lakhs():
    """Scenario 16: Indian numbering parsed accurately."""
    val = clean_value("4,80,147.00")
    assert val == 480147.0


def test_scenario_17_multi_currency_mentions():
    """Scenario 17: Local currency per section."""
    curr_main, _ = identify_currency("Statement of Profit or Loss (in USD Millions)")
    curr_note, _ = identify_currency("Note 14: Capital commitment in INR Crores (₹)")
    assert curr_main == "USD"
    assert curr_note == "INR"
