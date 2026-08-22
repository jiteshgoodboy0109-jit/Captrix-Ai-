"""
Comprehensive Apex Technologies Ltd Golden Benchmark Test Suite.
Validates all mandatory acceptance criteria for financial analysis accuracy.
"""

import io
import pandas as pd
import pytest
from app.engine.document_parser import (
    parse_workbook,
    classify_account,
    detect_year_columns,
    is_non_financial_header
)
from app.engine.canonical_model import build_canonical_dataset
from app.engine.statement_generator import (
    generate_financial_statements,
    generate_statements_for_year
)
from app.engine.financial_analyzer import (
    calculate_financial_ratios,
    calculate_corporate_finance
)
from app.engine.ai_insights import generate_ai_insights
from app.reports.excel_generator import generate_excel_report


def build_apex_mock_excel_bytes() -> bytes:
    """Generates in-memory Excel workbook containing Apex Technologies Ltd dataset."""
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
            ["Particulars", "Q1 FY2027"],
            ["Revenue from Operations", 30500],
            ["Other Income", 700],
            ["Net Profit for the Quarter", 5800]
        ]
        pd.DataFrame(q_data).to_excel(writer, sheet_name="Quarters", header=False, index=False)

    return output.getvalue()


def build_apex_mock_excel_bytes_out_of_order() -> bytes:
    """Generates workbook with out-of-order fiscal year columns (B=FY2026, C=FY2023, D=FY2024, E=FY2025)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pnl_data = [
            ["Apex Technologies Ltd. Financial Statements"],
            ["Particulars", "FY2026", "FY2023", "FY2024", "FY2025"],
            ["Revenue from Operations", 116000, 78000, 88000, 101000],
            ["Other Income", 2800, 1500, 2000, 2400],
            ["Cost of Goods Sold (COGS)", 42920, 31000, 35000, 38380],
            ["Operating Expenses", 37000, 22000, 25000, 28000],
            ["Depreciation & Amortization", 5700, 4000, 4800, 5200],
            ["Finance Costs / Interest Expense", 1900, 1200, 1500, 1700],
            ["Profit Before Tax (PBT)", 28480, 19300, 23700, 30120],
            ["Tax Expense", 7120, 4825, 5925, 7530],
            ["Net Profit for the Year", 21360, 14475, 17775, 22590]
        ]
        pd.DataFrame(pnl_data).to_excel(writer, sheet_name="Income Statement", header=False, index=False)
    return output.getvalue()


def test_1_source_parser_and_fiscal_year_detection():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    
    annual_years = sorted(list(set(i["year"] for i in parsed["normalized_items"] if i.get("year") and str(i.get("year")).isdigit() and not i.get("is_quarterly"))))
    assert annual_years == ["2023", "2024", "2025", "2026"], f"Expected ['2023', '2024', '2025', '2026'], got {annual_years}"


def test_2_fiscal_year_mapping_no_shift():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    items = parsed["normalized_items"]
    
    rev_2026 = [i for i in items if i.get("year") == "2026" and "revenue from operations" in str(i.get("account_name")).lower() and not i.get("is_quarterly")]
    assert len(rev_2026) > 0
    assert rev_2026[0]["net_amount"] == 116000.0, f"Expected 116000 for FY2026 Revenue, got {rev_2026[0]['net_amount']}"


def test_3_account_classification():
    assert classify_account("Goodwill") == "ASSET"
    assert classify_account("Intangible Assets") == "ASSET"
    assert classify_account("Profit Before Tax (PBT)") == "OPERATING_INCOME"
    assert classify_account("Tax Expense") == "TAX_EXPENSE"


def test_4_pnl_fy2026():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    
    by_year = stmts["by_year"]
    assert "2026" in by_year
    inc = by_year["2026"]["income_statement"]
    
    assert inc["sales"] == 116000.0
    assert inc["other_income"] == 2800.0
    assert inc["total_revenue"] == 118800.0
    assert inc["cost_of_goods_sold"] == 42920.0
    assert inc["gross_profit"] == 73080.0
    assert inc["ebitda"] == 36080.0
    assert inc["depreciation_amortization"] == 5700.0
    assert inc["ebit"] == 30380.0
    assert inc["interest_expense"] == 1900.0
    assert inc["ebt"] == 28480.0
    assert inc["tax_expense"] == 7120.0
    assert inc["net_income"] == 21360.0


def test_5_balance_sheet_fy2026():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    
    bs = stmts["by_year"]["2026"]["balance_sheet"]
    ca = bs["current_assets"]
    
    assert ca["cash"] == 20500.0
    assert ca["accounts_receivable"] == 20200.0
    assert ca["inventory"] == 9300.0
    assert ca["other_current_assets"] == 5200.0
    assert ca["total_current_assets"] == 55200.0
    
    assert bs["property_plant_equipment"]["net_property_plant_equipment"] == 29600.0
    assert bs["intangible_assets"]["goodwill"] == 6000.0
    assert bs["intangible_assets"]["trade_names"] == 5400.0
    assert bs["investment"] == 10500.0
    assert bs["other_assets"] == 3400.0
    assert bs["total_assets"] == 110100.0
    
    cl = bs["current_liabilities"]
    assert cl["accounts_payable"] == 10500.0
    assert cl["other_current_liabilities"] == 7600.0
    assert cl["short_term_debt"] == 2500.0
    assert cl["total_current_liabilities"] == 20600.0
    
    ltl = bs["long_term_liabilities"]
    assert ltl["long_term_debt"] == 9200.0
    assert ltl["other_non_current_liabilities"] == 4700.0
    assert bs["total_liabilities"] == 34500.0
    
    eq = bs["equity"]
    assert eq["common_stock"] == 10000.0
    assert eq["retained_earnings"] == 65600.0
    assert eq["total_equity"] == 75600.0
    assert bs["total_liabilities_and_equity"] == 110100.0


def test_6_ratio_engine_fy2026():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    ratios = calculate_financial_ratios(stmts["by_year"]["2026"])
    
    prof = ratios["profitability"]
    liq = ratios["liquidity"]
    solv = ratios["solvency"]
    
    assert abs(prof["gross_profit_margin"]["value"] - 61.52) < 0.1
    assert abs(prof["net_profit_margin"]["value"] - 17.98) < 0.1
    assert abs(liq["current_ratio"]["value"] - 2.68) < 0.05
    assert abs(solv["debt_to_equity"]["value"] - 0.15) < 0.05


def test_7_trial_balance_check():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    tb = stmts["by_year"]["2026"]["trial_balance"]
    
    assert tb["status"] in ["NOT_APPLICABLE", "PASS"]


def test_8_period_isolation_regression():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    items = parsed["normalized_items"]
    
    fy2026_items = [i for i in items if i.get("year") == "2026" and not i.get("is_quarterly")]
    q1_items = [i for i in items if i.get("is_quarterly")]
    
    fy2026_rev = sum(i["net_amount"] for i in fy2026_items if "revenue from operations" in str(i.get("account_name")).lower())
    q1_rev = sum(i["net_amount"] for i in q1_items if "revenue from operations" in str(i.get("account_name")).lower())
    
    assert fy2026_rev == 116000.0
    assert q1_rev == 30500.0
    assert (fy2026_rev + q1_rev) != 116000.0


def test_9_ai_consistency_and_narrative():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    canonical = build_canonical_dataset(parsed["normalized_items"], "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    target_stmts = stmts["by_year"]["2026"]
    ratios = calculate_financial_ratios(target_stmts)
    corp_fin = calculate_corporate_finance(target_stmts, ratios)
    
    ai_res = generate_ai_insights(target_stmts, ratios, corp_fin, canonical_dataset=canonical)
    summary = ai_res["executive_summary"]
    
    assert "$116,000.00" in summary
    assert "$21,360.00" in summary
    assert "3,899.40" not in summary


def test_10_excel_report_generation():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    canonical = build_canonical_dataset(parsed["normalized_items"], "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    target_stmts = stmts["by_year"]["2026"]
    ratios = calculate_financial_ratios(target_stmts)
    corp_fin = calculate_corporate_finance(target_stmts, ratios)
    ai_res = generate_ai_insights(target_stmts, ratios, corp_fin, canonical_dataset=canonical)
    
    report_bytes = generate_excel_report("Apex Technologies Ltd.", target_stmts, ratios, corp_fin, ai_res)
    assert len(report_bytes) > 0


def test_11_out_of_order_fiscal_year_headers():
    excel_bytes = build_apex_mock_excel_bytes_out_of_order()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_224.xlsx")
    items = parsed["normalized_items"]
    
    rev_2026 = [i for i in items if i.get("year") == "2026" and "revenue from operations" in str(i.get("account_name")).lower()]
    rev_2023 = [i for i in items if i.get("year") == "2023" and "revenue from operations" in str(i.get("account_name")).lower()]
    rev_2024 = [i for i in items if i.get("year") == "2024" and "revenue from operations" in str(i.get("account_name")).lower()]
    rev_2025 = [i for i in items if i.get("year") == "2025" and "revenue from operations" in str(i.get("account_name")).lower()]
    
    assert rev_2026[0]["net_amount"] == 116000.0
    assert rev_2023[0]["net_amount"] == 78000.0
    assert rev_2024[0]["net_amount"] == 88000.0
    assert rev_2025[0]["net_amount"] == 101000.0


def test_12_non_financial_header_filtering():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    items = parsed["normalized_items"]
    
    liab_eq_items = [i for i in items if "liabilities & equity" in str(i.get("account_name")).lower()]
    assert len(liab_eq_items) == 0, f"Expected 0 items for 'Liabilities & Equity', got {len(liab_eq_items)}"


def test_13_balance_sheet_equation_validation():
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    val_rep = stmts["by_year"]["2026"]["validation_report"]
    
    assert val_rep["balance_sheet_check"] == "PASS"
    assert val_rep["total_assets"] == 110100.0
    assert val_rep["total_liabilities_plus_equity"] == 110100.0


def test_14_roce_sanity_guard_protection():
    stmts = {
        "income_statement": {"ebit": 50000.0, "total_revenue": 100000.0},
        "balance_sheet": {
            "total_assets": 1000.0,
            "current_liabilities": {"total_current_liabilities": 2000.0},
            "equity": {"total_equity": -1000.0},
            "long_term_liabilities": {"total_long_term_liabilities": 0.0}
        }
    }
    ratios = calculate_financial_ratios(stmts)
    roce = ratios["profitability"]["return_on_capital_employed"]
    
    assert roce["is_calculable"] is False
    assert roce["display_value"] == "NOT_CALCULABLE"
    assert roce["status"] == "DATA_QUALITY_ERROR"


def test_15_master_validation_suite_runner():
    from app.engine.quality_engine import run_all_validations
    excel_bytes = build_apex_mock_excel_bytes()
    parsed = parse_workbook(excel_bytes, "Financial_Analysis_217.xlsx")
    canonical = build_canonical_dataset(parsed["normalized_items"], "Financial_Analysis_217.xlsx")
    stmts = generate_financial_statements(parsed["normalized_items"])
    target_stmts = stmts["by_year"]["2026"]
    ratios = calculate_financial_ratios(target_stmts)
    corp_fin = calculate_corporate_finance(target_stmts, ratios)
    ai_res = generate_ai_insights(target_stmts, ratios, corp_fin, canonical_dataset=canonical)
    
    val_summary = run_all_validations(canonical, stmts, ratios, ai_res)
    
    print("\n" + "=" * 50)
    for test_name, status in val_summary["test_results"].items():
        print(f"{test_name.replace('_', ' ')}: {status}")
    print("=" * 50)

    assert val_summary["all_tests_pass"] is True
    assert val_summary["final_status"] == "PASS"
