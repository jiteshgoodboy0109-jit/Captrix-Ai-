from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e_excel_upload_and_analysis():
    with open("sample_data/Acme_Corp_Financials_2025.xlsx", "rb") as f:
        response = client.post(
            "/api/upload/",
            files={"file": ("Acme_Corp_Financials_2025.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"company_name": "Acme Global Enterprise"}
        )
    
    assert response.status_code == 200
    res_data = response.json()
    assert "upload_id" in res_data
    upload_id = res_data["upload_id"]
    assert res_data["company_name"] == "Acme Global Enterprise"
    assert len(res_data["sheet_names"]) >= 3

    # Test Fetch Analysis Endpoint
    analysis_res = client.get(f"/api/analysis/{upload_id}")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert "statements" in analysis_data
    assert "ratios" in analysis_data
    assert "corporate_finance" in analysis_data
    assert "ai_report" in analysis_data

    # Test PDF Report Download
    pdf_res = client.get(f"/api/reports/pdf/{upload_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    # Test Excel Report Download
    excel_res = client.get(f"/api/reports/excel/{upload_id}")
    assert excel_res.status_code == 200
    assert "spreadsheet" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 1000

    # Test Chatbot Endpoint
    chat_res = client.post("/api/chat/", json={"upload_id": upload_id, "query": "Explain this Balance Sheet."})
    assert chat_res.status_code == 200
    assert "Balance Sheet" in chat_res.json()["response"]

    # Test History List
    hist_res = client.get("/api/history/")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1
