import io
import re
import pytest
import pandas as pd
import pypdf
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_generic_test_workbook() -> io.BytesIO:
    """Creates a generic multi-period financial workbook without any hardcoded test fixtures."""
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        bs_data = {
            "Account Name": [
                "Cash and Cash Equivalents",
                "Accounts Receivable",
                "Inventories",
                "Other Current Assets",
                "Total Current Assets",
                "Property, Plant and Equipment",
                "Intangible Assets",
                "Total Non-Current Assets",
                "Total Assets",
                "Accounts Payable",
                "Short-Term Borrowings",
                "Other Current Liabilities",
                "Total Current Liabilities",
                "Long-Term Debt",
                "Other Non-Current Liabilities",
                "Total Non-Current Liabilities",
                "Total Liabilities",
                "Common Stock",
                "Retained Earnings",
                "Total Shareholders Equity",
                "Total Liabilities and Equity"
            ],
            "2024": [
                150000.0, 220000.0, 180000.0, 30000.0, 580000.0,
                750000.0, 120000.0, 870000.0, 1450000.0,
                110000.0, 80000.0, 40000.0, 230000.0,
                320000.0, 50000.0, 370000.0, 600000.0,
                400000.0, 450000.0, 850000.0, 1450000.0
            ]
        }
        pd.DataFrame(bs_data).to_excel(writer, sheet_name="Balance Sheet", index=False)

        pl_data = {
            "Account Name": [
                "Revenue from Operations",
                "Cost of Goods Sold",
                "Gross Profit",
                "Selling and Marketing Expenses",
                "General and Administrative Expenses",
                "Operating Income (EBIT)",
                "Interest Expense",
                "Profit Before Tax",
                "Income Tax Expense",
                "Net Income"
            ],
            "2024": [
                1200000.0,
                700000.0,
                500000.0,
                140000.0,
                110000.0,
                250000.0,
                25000.0,
                225000.0,
                45000.0,
                180000.0
            ]
        }
        pd.DataFrame(pl_data).to_excel(writer, sheet_name="Income Statement", index=False)
    out.seek(0)
    return out

def test_production_request_chain_end_to_end():
    """
    Test the REAL production endpoint flow:
    1. Register/Login user -> JWT token
    2. POST /api/upload -> multipart file upload
    3. GET /api/analysis/{upload_id} -> verify calculation engine, ratios, and absence of prohibited terms
    4. GET /api/reports/pdf/{upload_id} -> verify generated PDF bytes contain authoritative ratios and 0 prohibited audit words
    5. GET /api/reports/excel/{upload_id} -> verify generated Excel bytes
    """
    import uuid
    random_email = f"reality_check_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "email": random_email,
        "full_name": "Reality Check Analyst",
        "password": "Password123!",
        "role": "Analyst"
    })
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Upload real generic workbook via production endpoint
    wb_bytes = create_generic_test_workbook().getvalue()
    upload_resp = client.post(
        "/api/upload",
        files={"file": ("Generic_Enterprise_Financials.xlsx", wb_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Apex Commercial Enterprises"},
        headers=headers
    )
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    upload_id = upload_resp.json()["upload_id"]
    assert upload_id is not None

    # Step 3: Call real production analysis endpoint
    analysis_resp = client.get(f"/api/analysis/{upload_id}", headers=headers)
    assert analysis_resp.status_code == 200, f"Analysis failed: {analysis_resp.text}"
    analysis_data = analysis_resp.json()

    # Verify Ratios in production response
    ratios = analysis_data.get("ratios", {})
    solv = ratios.get("solvency", {})
    liq = ratios.get("liquidity", {})

    # Debt-to-Equity
    assert "debt_to_equity" in solv, "debt_to_equity missing in solvency ratios"
    de = solv["debt_to_equity"]
    assert de["formula"] == "Interest-Bearing Debt / Shareholders' Equity", f"Incorrect D/E formula: {de['formula']}"
    assert "Total Liabilities" not in de["formula"]
    # Total debt = ST (80,000) + LT (320,000) = 400,000. Equity = 850,000 -> 400k/850k = 0.47
    assert abs(de["value"] - 0.47) <= 0.02, f"Expected D/E around 0.47, got {de['value']}"

    # Liabilities-to-Equity
    assert "liabilities_to_equity" in solv, "liabilities_to_equity missing in solvency ratios"
    lte = solv["liabilities_to_equity"]
    assert lte["formula"] == "Total Liabilities / Shareholders' Equity", f"Incorrect Liab/Equity formula: {lte['formula']}"
    # Total Liab = 600,000. Equity = 850,000 -> 600k/850k = 0.71
    assert abs(lte["value"] - 0.71) <= 0.02, f"Expected Liab/Equity around 0.71, got {lte['value']}"

    # Working Capital Ratio -> Net Working Capital to Revenue
    assert "working_capital_ratio" in liq, "working_capital_ratio missing in liquidity ratios"
    wc = liq["working_capital_ratio"]
    assert wc["name"] == "Net Working Capital to Revenue", f"Expected Net Working Capital to Revenue, got {wc['name']}"
    assert wc["formula"] == "(Current Assets - Current Liabilities) / Revenue", f"Incorrect formula: {wc['formula']}"
    # NWC = 580k - 230k = 350k. Revenue = 1,200k -> 350k/1200k = 29.17%
    assert abs(wc["value"] - 29.17) <= 0.5, f"Expected NWC to Revenue around 29.2%, got {wc['value']}"

    # Working Capital Cycle & Cash Conversion Cycle
    corp_fin = analysis_data.get("corporate_finance", {})
    wcc = corp_fin.get("working_capital_cycle", {})
    assert wcc.get("is_approximation") is True, "is_approximation must be True for single-period CCC"
    assert "Approximate" in wcc.get("metric_name", ""), f"metric_name should have Approximate, got {wcc.get('metric_name')}"

    # Verify absence of statutory audit claims in analysis payload
    from app.engine.output_validator import ReportConsistencyValidator
    violations = ReportConsistencyValidator.check_prohibited_audit_terminology(analysis_data)
    assert len(violations) == 0, f"Prohibited audit terminology found in production analysis: {violations}"

    # Step 4: Call real PDF report download endpoint
    pdf_resp = client.get(f"/api/reports/pdf/{upload_id}", headers=headers)
    assert pdf_resp.status_code == 200, f"PDF generation failed: {pdf_resp.text}"
    assert pdf_resp.headers.get("content-type") == "application/pdf"
    pdf_bytes = pdf_resp.content
    assert len(pdf_bytes) > 5000, "Generated PDF is suspiciously small"

    # Extract all text from generated PDF and perform strict audit check
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    all_pdf_text = ""
    for page in reader.pages:
        all_pdf_text += page.extract_text() or ""

    lower_pdf_text = all_pdf_text.lower()
    prohibited_in_pdf = [
        "statutory financial audit",
        "auditor's opinion",
        "clean bill of health",
        "isa / us gaas",
        "financial statements present fairly",
        "isa 320",
        "isa 700",
        "ai audit analysis"
    ]
    for term in prohibited_in_pdf:
        assert term not in lower_pdf_text, f"Prohibited term '{term}' found in production PDF!"

    # Ensure unqualified does not appear in opinion context
    assert "unqualified opinion" not in lower_pdf_text
    assert "unqualified" not in lower_pdf_text

    # Verify authoritative labels and formulas in PDF
    assert "Captrix AI Financial Analysis Report".lower() in lower_pdf_text
    assert "Interest-Bearing Debt / Shareholders' Equity".lower() in lower_pdf_text
    assert "Approximate Cash Conversion Cycle".lower() in lower_pdf_text
    assert "Net Working Capital to Revenue".lower() in lower_pdf_text

    # Step 5: Call real Excel report download endpoint
    excel_resp = client.get(f"/api/reports/excel/{upload_id}", headers=headers)
    assert excel_resp.status_code == 200, f"Excel generation failed: {excel_resp.text}"
    assert "spreadsheet" in excel_resp.headers.get("content-type")
    excel_bytes = excel_resp.content

    xl = pd.ExcelFile(io.BytesIO(excel_bytes))
    assert "Ratio Analysis" in xl.sheet_names
    assert "Working Capital & CCC" in xl.sheet_names

    ratio_df = xl.parse("Ratio Analysis")
    assert isinstance(ratio_df, pd.DataFrame)
    de_row = ratio_df[ratio_df["Ratio Name"].astype(str).str.contains("Debt to Equity", case=False)]
    assert not de_row.empty, "Debt to Equity row missing in Excel report"
    assert de_row.iloc[0]["Formula"] == "Interest-Bearing Debt / Shareholders' Equity"
