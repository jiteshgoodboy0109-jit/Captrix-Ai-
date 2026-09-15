import io
import uuid
import random
import pytest
import pandas as pd
import pypdf
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_unseen_balanced_company(seed: int = 42) -> io.BytesIO:
    """
    Dynamically generates an unseen corporate workbook with randomized figures.
    No values or company names are hardcoded in the application code.
    """
    rng = random.Random(seed)
    
    # Random base operational scales
    rev = rng.randint(800, 2500) * 1000.0
    cogs = round(rev * rng.uniform(0.50, 0.65), 2)
    gp = round(rev - cogs, 2)
    s_m = round(rev * rng.uniform(0.08, 0.12), 2)
    g_a = round(rev * rng.uniform(0.06, 0.10), 2)
    depr = round(rev * rng.uniform(0.03, 0.05), 2)
    ebit = round(gp - s_m - g_a - depr, 2)
    interest_exp = round(rev * rng.uniform(0.01, 0.03), 2)
    other_inc = round(rev * rng.uniform(0.005, 0.02), 2)
    pbt = round(ebit + other_inc - interest_exp, 2)
    tax = round(pbt * 0.25, 2)
    net_inc = round(pbt - tax, 2)

    # Balance Sheet items
    cash = round(rev * rng.uniform(0.10, 0.20), 2)
    ar = round(rev * rng.uniform(0.12, 0.18), 2)
    inv = round(cogs * rng.uniform(0.15, 0.25), 2)
    other_ca = round(rev * 0.02, 2)
    total_ca = round(cash + ar + inv + other_ca, 2)

    ppe = round(rev * rng.uniform(0.40, 0.70), 2)
    intangibles = round(rev * rng.uniform(0.05, 0.15), 2)
    total_nca = round(ppe + intangibles, 2)
    total_assets = round(total_ca + total_nca, 2)

    ap = round(cogs * rng.uniform(0.10, 0.18), 2)
    st_debt = round(rev * rng.uniform(0.04, 0.08), 2)
    other_cl = round(rev * 0.02, 2)
    total_cl = round(ap + st_debt + other_cl, 2)

    lt_debt = round(rev * rng.uniform(0.15, 0.30), 2)
    other_ncl = round(rev * 0.03, 2)
    total_ncl = round(lt_debt + other_ncl, 2)
    total_liab = round(total_cl + total_ncl, 2)

    # Permanent equity balances
    total_equity = round(total_assets - total_liab, 2)
    common_stock = round(total_equity * 0.45, 2)
    retained_earnings = round(total_equity - common_stock, 2)

    # Cash Flow Statement items
    ocf = round(net_inc + depr - (ar * 0.05) + (ap * 0.03), 2)
    icf = round(-(ppe * 0.15), 2)
    fcf = round(-(interest_exp + st_debt * 0.10), 2)
    net_cash_flow = round(ocf + icf + fcf, 2)

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        bs_df = pd.DataFrame({
            "Line Item": [
                "Cash and Cash Equivalents",
                "Trade and Other Receivables",
                "Inventories",
                "Other Current Assets",
                "Total Current Assets",
                "Property Plant and Equipment",
                "Intangible Assets",
                "Total Non-Current Assets",
                "Total Assets",
                "Trade Payables",
                "Short-Term Borrowings",
                "Other Current Liabilities",
                "Total Current Liabilities",
                "Long-Term Debt",
                "Other Non-Current Liabilities",
                "Total Non-Current Liabilities",
                "Total Liabilities",
                "Common Stock",
                "Retained Earnings",
                "Total Shareholders' Equity",
                "Total Liabilities and Equity"
            ],
            "Period 2024": [
                cash, ar, inv, other_ca, total_ca,
                ppe, intangibles, total_nca, total_assets,
                ap, st_debt, other_cl, total_cl,
                lt_debt, other_ncl, total_ncl, total_liab,
                common_stock, retained_earnings, total_equity,
                round(total_liab + total_equity, 2)
            ]
        })
        bs_df.to_excel(writer, sheet_name="Balance Sheet", index=False)

        pl_df = pd.DataFrame({
            "Line Item": [
                "Revenue from Operations",
                "Cost of Goods Sold",
                "Gross Profit",
                "Selling and Marketing Expenses",
                "General and Administrative Expenses",
                "Depreciation & Amortization",
                "Operating Income (EBIT)",
                "Interest Expense",
                "Other Income",
                "Profit Before Tax",
                "Income Tax Expense",
                "Net Income"
            ],
            "Period 2024": [
                rev, cogs, gp, s_m, g_a, depr, ebit, interest_exp, other_inc, pbt, tax, net_inc
            ]
        })
        pl_df.to_excel(writer, sheet_name="Income Statement", index=False)

        cf_df = pd.DataFrame({
            "Cash Flow Line": [
                "Net Cash from Operating Activities",
                "Net Cash used in Investing Activities",
                "Net Cash used in Financing Activities",
                "Net Change in Cash"
            ],
            "Period 2024": [
                ocf, icf, fcf, net_cash_flow
            ]
        })
        cf_df.to_excel(writer, sheet_name="Cash Flows", index=False)

    out.seek(0)
    return out

def create_unseen_inconsistent_company() -> io.BytesIO:
    """Creates an unseen workbook with deliberate arithmetic mismatches in source."""
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        # Deliberate Gross Profit mismatch: 1,000,000 - 600,000 != 550,000
        pl_df = pd.DataFrame({
            "Line Item": [
                "Revenue from Operations",
                "Cost of Goods Sold",
                "Gross Profit",
                "Net Income"
            ],
            "2024": [1000000.0, 600000.0, 550000.0, 150000.0]
        })
        pl_df.to_excel(writer, sheet_name="Income Statement", index=False)

        # Deliberate Balance Sheet imbalance: Assets 900k != Liab 400k + Equity 450k (850k)
        bs_df = pd.DataFrame({
            "Line Item": [
                "Cash and Cash Equivalents",
                "Accounts Receivable",
                "Total Current Assets",
                "Total Assets",
                "Accounts Payable",
                "Total Current Liabilities",
                "Long-Term Debt",
                "Total Liabilities",
                "Common Stock",
                "Total Equity",
                "Total Liabilities and Equity"
            ],
            "2024": [
                300000.0, 600000.0, 900000.0, 900000.0,
                200000.0, 200000.0, 200000.0, 400000.0,
                450000.0, 450000.0, 850000.0
            ]
        })
        bs_df.to_excel(writer, sheet_name="Balance Sheet", index=False)
    out.seek(0)
    return out

def create_unseen_service_company_no_inventory() -> io.BytesIO:
    """Creates an unseen service company with no inventory and no cash flow statement."""
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        pl_df = pd.DataFrame({
            "Account": [
                "Service Revenues",
                "Operating Expenses",
                "Operating Income",
                "Net Profit"
            ],
            "FY2024": [500000.0, 320000.0, 180000.0, 140000.0]
        })
        pl_df.to_excel(writer, sheet_name="P&L", index=False)

        bs_df = pd.DataFrame({
            "Account": [
                "Cash at Bank",
                "Accounts Receivable",
                "Total Current Assets",
                "Total Assets",
                "Accounts Payable",
                "Total Current Liabilities",
                "Total Liabilities",
                "Shareholder Capital",
                "Retained Earnings",
                "Total Equity",
                "Total Liabilities & Equity"
            ],
            "FY2024": [
                120000.0, 80000.0, 200000.0, 200000.0,
                50000.0, 50000.0, 50000.0,
                100000.0, 50000.0, 150000.0, 200000.0
            ]
        })
        bs_df.to_excel(writer, sheet_name="BS", index=False)
    out.seek(0)
    return out

def get_auth_token() -> str:
    email = f"analyst_{uuid.uuid4().hex[:8]}@universal-audit.org"
    reg = client.post("/api/auth/register", json={
        "email": email,
        "full_name": "Senior Verification Analyst",
        "password": "Password123!",
        "role": "Lead Partner"
    })
    return reg.json()["access_token"]

def test_unseen_dataset_balanced_industrial_core_capabilities():
    """
    Capability 1: P&L reconstruction (Gross Profit, Operating Profit, PBT, Net Profit)
    Capability 2: Balance Sheet reconstruction (Assets = Liabilities + Equity)
    Capability 3: Cash Flow reconstruction & Cash reconciliation
    Capability 4: Core ratio calculation & formula/value agreement
    """
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    wb_stream = create_unseen_balanced_company(seed=101)
    upload_res = client.post(
        "/api/upload",
        files={"file": ("Vanguard_Engineering_2024.xlsx", wb_stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Vanguard Engineering Holdings"},
        headers=headers
    )
    assert upload_res.status_code == 200
    upload_id = upload_res.json()["upload_id"]

    analysis_res = client.get(f"/api/analysis/{upload_id}", headers=headers)
    assert analysis_res.status_code == 200
    payload = analysis_res.json()

    # 1. P&L Reconstruction Verification
    inc = payload["statements"]["income_statement"]
    rev = inc.get("total_revenue")
    cogs = inc.get("cost_of_goods_sold")
    gp = inc.get("gross_profit")
    ebit = inc.get("ebit")
    pbt = inc.get("pbt")
    net_profit = inc.get("net_profit")

    op_rev = inc.get("revenue_from_operations") or inc.get("sales") or rev
    assert op_rev is not None and op_rev > 0
    assert cogs is not None and cogs > 0
    assert gp is not None
    assert abs(round(op_rev - cogs, 2) - gp) <= 1.0, f"Gross Profit mismatch: {op_rev} - {cogs} != {gp}"
    assert ebit is not None
    assert pbt is not None
    assert net_profit is not None

    # 2. Balance Sheet Reconstruction & Identity Verification
    bs = payload["statements"]["balance_sheet"]
    tot_assets = bs.get("total_assets")
    tot_liab = bs.get("total_liabilities")
    tot_eq = bs.get("equity", {}).get("total_equity")
    val_report = payload["statements"]["validation_report"]

    assert tot_assets is not None and tot_assets > 0
    assert tot_liab is not None and tot_liab > 0
    assert tot_eq is not None and tot_eq > 0
    assert abs(round(tot_assets - (tot_liab + tot_eq), 2)) <= 1.0, "Accounting Equation failed"
    assert val_report["balance_sheet_check"] == "PASS"
    assert val_report["is_balanced"] is True

    # 3. Cash Flow Reconciliation Verification
    cf = payload["statements"]["cash_flow"]
    assert cf.get("status") == "Available"
    assert cf.get("operating_activities") is not None
    assert cf.get("investing_activities") is not None
    assert cf.get("financing_activities") is not None
    expected_cf_net = round(cf["operating_activities"] + cf["investing_activities"] + cf["financing_activities"], 2)
    assert abs(cf.get("net_change_in_cash") - expected_cf_net) <= 1.0

    # 4. Core Ratio Formula & Value Consistency
    ratios = payload["ratios"]
    solv = ratios["solvency"]
    liq = ratios["liquidity"]
    prof = ratios["profitability"]

    # Current Ratio
    cr = liq["current_ratio"]
    assert cr["is_calculable"] is True
    assert cr["formula"] == "Current Assets / Current Liabilities"
    ca_val = cr["inputs"]["Current Assets"]
    cl_val = cr["inputs"]["Current Liabilities"]
    assert abs(round(ca_val / cl_val, 2) - cr["value"]) <= 0.02

    # Debt to Equity
    de = solv["debt_to_equity"]
    assert de["is_calculable"] is True
    assert de["formula"] == "Interest-Bearing Debt / Shareholders' Equity"
    debt_inputs = de["inputs"]["Interest-Bearing Debt"]
    eq_input = de["inputs"]["Shareholders' Equity"]
    assert abs(round(debt_inputs / eq_input, 2) - de["value"]) <= 0.02

    # Liabilities to Equity
    lte = solv["liabilities_to_equity"]
    assert lte["is_calculable"] is True
    assert lte["formula"] == "Total Liabilities / Shareholders' Equity"
    assert abs(round(tot_liab / tot_eq, 2) - lte["value"]) <= 0.02

    # Net Working Capital to Revenue
    nwc_r = liq["working_capital_ratio"]
    assert nwc_r["is_calculable"] is True
    assert nwc_r["name"] == "Net Working Capital to Revenue"
    assert nwc_r["formula"] == "(Current Assets - Current Liabilities) / Revenue"
    nwc_val = nwc_r["inputs"]["Net Working Capital"]
    rev_val = nwc_r["inputs"]["Revenue"]
    assert abs(round((nwc_val / rev_val) * 100.0, 2) - nwc_r["value"]) <= 0.1

    # Gross Margin
    gpm = prof["gross_profit_margin"]
    assert gpm["is_calculable"] is True
    assert abs(round((gp / rev) * 100.0, 2) - gpm["value"]) <= 0.1

    # Net Profit Margin
    npm = prof["net_profit_margin"]
    assert npm["is_calculable"] is True
    assert abs(round((net_profit / rev) * 100.0, 2) - npm["value"]) <= 0.1

def test_unseen_inconsistency_detection_and_source_preservation():
    """
    Capability 5: Inconsistency detection (Balance sheet imbalance & P&L arithmetic mismatch)
    Capability 6: Source-value preservation (reported values are preserved without synthetic alteration)
    """
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    wb_stream = create_unseen_inconsistent_company()
    upload_res = client.post(
        "/api/upload",
        files={"file": ("Flawed_Accounting_Records.xlsx", wb_stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Flawed Ledger Corp"},
        headers=headers
    )
    assert upload_res.status_code == 200
    upload_id = upload_res.json()["upload_id"]

    analysis_res = client.get(f"/api/analysis/{upload_id}", headers=headers)
    assert analysis_res.status_code == 200
    payload = analysis_res.json()

    # Verify Inconsistency Detection in Balance Sheet
    bs = payload["statements"]["balance_sheet"]
    val_report = payload["statements"]["validation_report"]
    assert val_report["balance_sheet_check"] == "UNBALANCED"
    assert val_report["is_balanced"] is False
    assert val_report["difference"] == 50000.0, f"Expected 50,000 difference, got {val_report['difference']}"

    # Verify Source Value Preservation: Reported assets must remain 900,000
    assert bs["total_assets"] == 900000.0
    assert bs["total_liabilities"] == 400000.0
    assert bs["equity"]["total_equity"] == 450000.0

    # Verify P&L Arithmetic Mismatch Detection: Source GP 550,000 != 1,000,000 - 600,000 (400,000)
    inc = payload["statements"]["income_statement"]
    assert inc["gross_profit"] == 550000.0  # Preserved from source
    assert inc["gross_profit_status"] == "MISMATCH"
    assert inc["gross_profit_calculated"] == 400000.0
    assert abs(inc["gross_profit_variance"] - 150000.0) <= 1.0

def test_unseen_missing_value_handling_service_company():
    """
    Capability 7: Missing-value handling (Service company without inventory or cash flow)
    Ratios dependent on missing inventory or cash flow must be cleanly marked not calculable.
    """
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    wb_stream = create_unseen_service_company_no_inventory()
    upload_res = client.post(
        "/api/upload",
        files={"file": ("Cloud_Consulting_Services.xlsx", wb_stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Cloud Advisory LLC"},
        headers=headers
    )
    assert upload_res.status_code == 200
    upload_id = upload_res.json()["upload_id"]

    analysis_res = client.get(f"/api/analysis/{upload_id}", headers=headers)
    assert analysis_res.status_code == 200
    payload = analysis_res.json()

    # Cash Flow should be marked Not Available in Source Workbook or NOT_REPORTED_IN_SOURCE (not fabricated)
    cf = payload["statements"]["cash_flow"]
    assert cf["status"] in ["NOT_REPORTED_IN_SOURCE", "Not Available in Source Workbook"]
    assert cf.get("operating_activities") is None
    assert cf.get("net_change_in_cash") is None

    # Inventory Turnover must NOT fabricate an answer
    ratios = payload["ratios"]
    inv_t = ratios["efficiency"]["inventory_turnover"]
    assert inv_t["is_calculable"] is False
    assert inv_t["value"] is None
    assert "Not Calculable" in inv_t["display_value"]

    # Working capital ratio (Net Working Capital to Revenue) remains calculable from CA, CL, and Revenue
    wc_r = ratios["liquidity"]["working_capital_ratio"]
    assert wc_r["is_calculable"] is True
    # NWC = 200k - 50k = 150k. Revenue = 500k -> 150k/500k = 30.0%
    assert abs(wc_r["value"] - 30.0) <= 0.1

def test_unseen_production_pdf_excel_generation():
    """
    Capability 8: Production PDF and Excel generation from unseen calculations.
    Ensures PDF and Excel render without error and contain no prohibited terms.
    """
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    wb_stream = create_unseen_balanced_company(seed=777)
    upload_res = client.post(
        "/api/upload",
        files={"file": ("Unseen_Global_Logistics.xlsx", wb_stream.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Global Freight & Logistics"},
        headers=headers
    )
    assert upload_res.status_code == 200
    upload_id = upload_res.json()["upload_id"]

    # Download PDF
    pdf_res = client.get(f"/api/reports/pdf/{upload_id}", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 5000

    # Verify PDF text
    reader = pypdf.PdfReader(io.BytesIO(pdf_res.content))
    all_text = ""
    for p in reader.pages:
        all_text += p.extract_text() or ""
    lower = all_text.lower()

    assert "statutory financial audit" not in lower
    assert "auditor's opinion" not in lower
    assert "unqualified" not in lower
    assert "clean bill of health" not in lower
    assert "isa 320" not in lower
    assert "isa 700" not in lower
    assert "Global Freight & Logistics".lower() in lower
    assert "Captrix AI Financial Analysis Report".lower() in lower

    # Download Excel
    excel_res = client.get(f"/api/reports/excel/{upload_id}", headers=headers)
    assert excel_res.status_code == 200
    assert "spreadsheet" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 3000
