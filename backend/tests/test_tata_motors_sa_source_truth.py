import pytest
import io
import pandas as pd
from app.engine.document_parser import parse_workbook, identify_currency
from app.engine.statement_generator import generate_financial_statements
from app.engine.currency_engine import SUPPORTED_CURRENCIES, format_currency_amount

def test_tata_motors_sa_exact_pipeline():
    """
    Verifies the universal architecture against Tata Motors (SA) Proprietary Limited Annual Accounts:
    - Entity: Tata Motors (SA) Proprietary Limited
    - Currency: South African Rand (R) -> ZAR
    - Reporting Periods: FY2022 & FY2021 (31 March 2022 / 31 March 2021)
    - Statements: Balance Sheet (Statement of Financial Position), P&L (Statement of Profit or Loss and OCI), Cash Flow, Changes in Equity
    - Exact Reconciliations: Assets = Equity + Liabilities (169,222,313), Zero P&L derivation variance.
    """
    
    # 1. Currency identification checks
    curr, mult = identify_currency("Figures in South African Rand (R), unless otherwise stated.")
    assert curr == "ZAR", f"Expected ZAR but got {curr}"
    assert mult == 1.0
    
    curr2, mult2 = identify_currency("2022 (R)")
    assert curr2 == "ZAR", f"Expected ZAR but got {curr2}"

    # 2. Mock workbook structure matching the exact South African annual accounts
    pnl_df = pd.DataFrame([
        {"Particulars": "Statement of Profit or Loss and Other Comprehensive Income", "2022": None, "2021": None},
        {"Particulars": "Figures in South African Rand (R), unless otherwise stated.", "2022": None, "2021": None},
        {"Particulars": "Revenue", "2022": 330189883, "2021": 295000000},
        {"Particulars": "Cost of sales", "2022": 309779307, "2021": 278000000},
        {"Particulars": "Gross profit", "2022": 20410576, "2021": 17000000},
        {"Particulars": "Other income", "2022": 1394656, "2021": 1100000},
        {"Particulars": "Operating expenses", "2022": 8829872, "2021": 7500000},
        {"Particulars": "Profit from operations", "2022": 12975360, "2021": 10600000},
        {"Particulars": "Interest received", "2022": 958687, "2021": 800000},
        {"Particulars": "Finance costs", "2022": 1248878, "2021": 1150000},
        {"Particulars": "Profit before taxation", "2022": 12685169, "2021": 10250000},
        {"Particulars": "Taxation", "2022": 4210658, "2021": 3400000},
        {"Particulars": "Profit for the year", "2022": 8474511, "2021": 6850000},
    ])

    bs_df = pd.DataFrame([
        {"Particulars": "Statement of Financial Position", "2022": None, "2021": None},
        {"Particulars": "Figures in South African Rand (R), unless otherwise stated.", "2022": None, "2021": None},
        {"Particulars": "Property, plant and equipment", "2022": 45000000, "2021": 42000000},
        {"Particulars": "Intangible assets", "2022": 5000000, "2021": 5000000},
        {"Particulars": "Inventories", "2022": 42222313, "2021": 38000000},
        {"Particulars": "Trade and other receivables", "2022": 52000000, "2021": 48000000},
        {"Particulars": "Cash and cash equivalents", "2022": 25000000, "2021": 20000000},
        {"Particulars": "Total Assets", "2022": 169222313, "2021": 153000000},
        {"Particulars": "Share capital", "2022": 50000000, "2021": 50000000},
        {"Particulars": "Retained income", "2022": 39222313, "2021": 30747802},
        {"Particulars": "Total Equity", "2022": 89222313, "2021": 80747802},
        {"Particulars": "Long-term borrowings", "2022": 30000000, "2021": 28000000},
        {"Particulars": "Trade and other payables", "2022": 50000000, "2021": 44252198},
        {"Particulars": "Total Liabilities", "2022": 80000000, "2021": 72252198},
        {"Particulars": "Total Equity and Liabilities", "2022": 169222313, "2021": 153000000},
    ])

    cf_df = pd.DataFrame([
        {"Particulars": "Statement of Cash Flows", "2022": None, "2021": None},
        {"Particulars": "Cash generated from operating activities", "2022": 15000000, "2021": 12000000},
        {"Particulars": "Cash flows from investing activities", "2022": -5000000, "2021": -4000000},
        {"Particulars": "Cash flows from financing activities", "2022": -5000000, "2021": -3000000},
        {"Particulars": "Net increase in cash and cash equivalents", "2022": 5000000, "2021": 5000000},
    ])

    # Save to Excel bytes
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        pnl_df.to_excel(writer, sheet_name="Statement of Profit or Loss", index=False)
        bs_df.to_excel(writer, sheet_name="Financial Position", index=False)
        cf_df.to_excel(writer, sheet_name="Cash Flows", index=False)
    file_bytes = excel_buf.getvalue()

    # 3. Parse workbook
    parsed = parse_workbook(file_bytes, "Tata_Motors_SA_Proprietary_Limited_Annual_Accounts_2022.xlsx")

    assert parsed["currency"] == "ZAR", f"Expected currency ZAR, got {parsed['currency']}"
    assert "Tata Motors (SA) Proprietary Limited" in parsed["company_name"] or "Tata Motors Sa Proprietary Limited" in parsed["company_name"]

    # 4. Generate financial statements
    stmt_result = generate_financial_statements(parsed["normalized_items"])
    
    pnl = stmt_result["income_statement"]
    bs = stmt_result["balance_sheet"]
    cf = stmt_result["cash_flow"]

    # Statement Presence
    assert bs["status"] == "PASS", f"Balance Sheet status expected PASS, got {bs.get('status')}"
    assert cf["status"] == "Available", f"Cash Flow status expected Available, got {cf.get('status')}"

    # P&L Figures & Zero Variance Check
    assert pnl["revenue_from_operations"] == 330189883.0
    assert pnl["cost_of_goods_sold"] == 309779307.0
    assert pnl["gross_profit"] == 20410576.0
    assert pnl["other_income"] == 1394656.0
    assert pnl["operating_expenses"] == 8829872.0
    assert pnl["profit_from_operations"] == 12975360.0
    assert pnl["interest_income"] == 958687.0
    assert pnl["interest_expense"] == 1248878.0
    assert pnl["pbt"] == 12685169.0
    assert pnl["tax_expense"] == 4210658.0
    assert pnl["net_income"] == 8474511.0
    assert pnl["net_income_reconciliation_status"] == "VERIFIED"

    # Balance Sheet Equality Check
    assert bs["total_assets"] == 169222313.0
    assert bs["total_liabilities"] == 80000000.0
    assert bs["equity"]["total_equity"] == 89222313.0
    assert bs["total_liabilities_and_equity"] == 169222313.0
    assert abs(bs["total_assets"] - bs["total_liabilities_and_equity"]) == 0.0

    # Multi-period extraction check
    assert "FY2022" in stmt_result["by_year"]
    assert "FY2021" in stmt_result["by_year"]
