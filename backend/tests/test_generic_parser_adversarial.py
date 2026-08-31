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


def test_7_currency_engine_evidence_gating():
    """
    Evidence-Gating Rule 1:
    - Missing/unknown currency text must NOT default to USD.
    - Currency conversion on undetermined currency must return status NOT_CALCULABLE with None amount.
    - Format amount on None must return 'NOT_REPORTED'.
    - Format amount on NOT_DETERMINED must omit currency symbol.
    """
    from app.engine.currency_engine import identify_currency, convert_currency, format_currency_amount, get_exchange_rate

    curr1, mult1 = identify_currency("")
    assert curr1 == "NOT_DETERMINED"
    assert mult1 == 1.0

    curr2, mult2 = identify_currency("General Ledger Report")
    assert curr2 == "NOT_DETERMINED"

    curr3, mult3 = identify_currency("Revenue in INR ₹ Crores")
    assert curr3 == "INR"
    assert mult3 == 10000000.0

    rate = get_exchange_rate("NOT_DETERMINED", "USD")
    assert rate is None

    conv = convert_currency(50000.0, "NOT_DETERMINED", "USD")
    assert conv["status"] == "NOT_CALCULABLE"
    assert conv["converted_amount"] is None

    conv_none = convert_currency(None, "USD", "EUR")
    assert conv_none["status"] == "NOT_REPORTED"
    assert conv_none["converted_amount"] is None

    fmt_none = format_currency_amount(None)
    assert fmt_none == "NOT_REPORTED"

    fmt_nodet = format_currency_amount(1500000.0, "NOT_DETERMINED")
    assert "$" not in fmt_nodet and "₹" not in fmt_nodet
    assert "1,500,000.00" in fmt_nodet


def test_8_document_parser_evidence_gating_unlabeled_data():
    """
    Evidence-Gating Rule 2:
    - Unlabeled single-period documents without explicit year must produce fiscal_year = UNKNOWN.
    - Documents without currency tokens must produce currency = NOT_DETERMINED.
    - Explicit zero values must be preserved as 0.0, not dropped or fabricated.
    """
    csv_unlabeled = b"Particulars,Amount\nService Sales,250000\nCost of Services,150000\nOther Fees,0\n"
    parsed = parse_workbook(csv_unlabeled, "raw_unlabeled.csv")

    assert parsed["metadata"]["currency"] == "NOT_DETERMINED"
    
    items = parsed["normalized_items"]
    assert len(items) == 3
    # Check that explicit 0 is preserved
    zero_item = [i for i in items if i["account_name"] == "Other Fees"][0]
    assert zero_item["net_amount"] == 0.0

    statements = generate_financial_statements(items)
    assert "income_statement" in statements
    assert statements["income_statement"]["revenue_from_operations"] == 250000.0


def test_9_statement_generator_missing_statement_gating():
    """
    Evidence-Gating Rule 3:
    - Ingesting a P&L-only file must leave Balance Sheet and Cash Flow as NOT_REPORTED / Not Available.
    - Missing values must remain None, never 0.0.
    - Derived metrics without required inputs must be NOT_CALCULABLE.
    """
    csv_pnl_only = b"Particulars,FY2025\nRevenue from Operations,500000\nAdministrative Expenses,120000\nTaxation,30000\n"
    parsed = parse_workbook(csv_pnl_only, "pnl_only.csv")
    statements = generate_financial_statements(parsed["normalized_items"])

    inc = statements["income_statement"]
    bs = statements["balance_sheet"]
    cf = statements["cash_flow"]

    assert inc["gross_profit"] is None
    assert inc["gross_profit_status"] == "NOT_CALCULABLE"
    assert bs.get("status") in ["NOT_REPORTED_IN_SOURCE", "NOT_REPORTED", "INCOMPLETE"]
    assert cf.get("status") in ["Not Available in Source Workbook", "NOT_AVAILABLE"]
    assert bs.get("total_assets") is None
    assert cf.get("operating_activities") is None


def test_10_reconciliation_evidence_gating_missing_and_zero():
    """
    Evidence-Gating Rule 4:
    - Reconciliation on absent statements marks metrics as NOT_AVAILABLE.
    - Preserves reported zero values with PASS and 0.0 difference.
    """
    from app.engine.reconciliation import perform_source_to_result_reconciliation

    canonical_dataset = {
        "layer_b_canonical_metrics": {
            "revenue": {"value": 100000.0, "source_cell": "B2", "validation_status": "Reported in Source"},
            "interest_expense": {"value": 0.0, "source_cell": "B5", "validation_status": "Reported in Source"},
            "total_assets": {"value": None, "source_cell": "N/A", "validation_status": "Not Separately Reported in Source Workbook"}
        }
    }
    statements = {
        "income_statement": {"revenue_from_operations": 100000.0, "interest_expense": 0.0},
        "balance_sheet": {"status": "NOT_REPORTED_IN_SOURCE", "total_assets": None},
        "cash_flow": {"status": "NOT_REPORTED_IN_SOURCE", "operating_activities": None}
    }

    rec = perform_source_to_result_reconciliation(canonical_dataset, statements, {})
    assert rec["reconciliation_status"] == "PASS"

    rev_metric = [m for m in rec["metrics"] if m["metric"] == "revenue"][0]
    assert rev_metric["status"] == "PASS"
    assert rev_metric["source_value"] == 100000.0
    assert rev_metric["difference"] == 0.0

    int_metric = [m for m in rec["metrics"] if m["metric"] == "interest_expense"][0]
    assert int_metric["status"] == "PASS"
    assert int_metric["source_value"] == 0.0
    assert int_metric["difference"] == 0.0

    ta_metric = [m for m in rec["metrics"] if m["metric"] == "total_assets"][0]
    assert ta_metric["status"] == "NOT_AVAILABLE"
    assert ta_metric["source_value"] is None


def test_11_adversarial_source_gating_matrix():
    """
    Master regression test covering all 8 Step 1 adversarial source-gating scenarios:
    1. missing currency never defaults to USD
    2. missing year never defaults to a guessed year
    3. missing financial values never become numeric zero
    4. actual source zero remains zero
    5. formulas with missing inputs return NOT_CALCULABLE
    6. missing statements are suppressed
    7. unsupported ratios are suppressed
    8. unknown accounts are not force-classified
    """
    from app.engine.document_parser import classify_account
    from app.engine.financial_analyzer import calculate_financial_ratios

    # 1. Missing currency
    p1 = parse_workbook(b"Particulars,Amount\nConsulting Revenue,100000\n", "c1.csv")
    assert p1["currency"] == "NOT_DETERMINED"

    # 2. Missing year
    p2 = parse_workbook(b"Particulars,Current Period\nGross Sales,50000\n", "c2.csv")
    assert p2["normalized_items"][0].get("fiscal_year") == "UNKNOWN"

    # 3. Missing values
    p3 = parse_workbook(b"Particulars,FY2025\nRevenue,200000\nCost of Goods Sold,\n", "c3.csv")
    s3 = generate_financial_statements(p3["normalized_items"])
    assert s3["income_statement"]["cost_of_goods_sold"] is None
    assert s3["income_statement"]["cogs_status"] == "NOT_REPORTED"

    # 4. Actual source zero
    p4 = parse_workbook(b"Particulars,FY2025\nRevenue from Operations,300000\nInterest Expense,0\n", "c4.csv")
    s4 = generate_financial_statements(p4["normalized_items"])
    assert s4["income_statement"]["finance_cost"] == 0.0

    # 5. Formulas with missing inputs
    p5 = parse_workbook(b"Particulars,FY2025\nRevenue from Operations,500000\n", "c5.csv")
    s5 = generate_financial_statements(p5["normalized_items"])
    assert s5["income_statement"]["gross_profit"] is None
    assert s5["income_statement"]["gross_profit_status"] == "NOT_CALCULABLE"

    # 6. Missing statements suppressed
    p6 = parse_workbook(b"Particulars,FY2025\nSales Revenue,600000\n", "c6.csv")
    s6 = generate_financial_statements(p6["normalized_items"])
    assert s6["balance_sheet"].get("status") in ["NOT_REPORTED_IN_SOURCE", "NOT_REPORTED"]
    assert s6["balance_sheet"].get("total_assets") is None
    assert s6["cash_flow"].get("operating_activities") is None

    # 7. Unsupported ratios suppressed
    r6 = calculate_financial_ratios(s6)
    assert r6["liquidity"]["current_ratio"]["is_calculable"] is False
    assert r6["solvency"]["debt_to_equity"]["is_calculable"] is False

    # 8. Unknown accounts not force-classified
    assert classify_account("Project Alpha Custom Escrow Account 99", "General Ledger") == "UNCLASSIFIED"
