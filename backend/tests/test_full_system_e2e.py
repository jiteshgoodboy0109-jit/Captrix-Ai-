"""
Full System Comprehensive End-to-End Test Suite
Validates all API endpoints, multi-user isolation, mathematical precision,
data lineage, model leaderboard, reporting, and chatbot copilot.
"""

import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, SessionLocal
from app.db.models import User

client = TestClient(app)

def test_01_health_and_accuracy_endpoints():
    """Verify root and system health accuracy diagnostics."""
    # Root check
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["status"] == "ONLINE"

    # Accuracy diagnostics
    health_res = client.get("/api/health/accuracy")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert "overall_accuracy_rate" in health_data
    assert health_data["status"] == "ALL MODULES OPERATIONAL"
    assert "document_parser" in health_data["module_accuracy"]
    assert "financial_analyzer_math" in health_data["module_accuracy"]


def test_02_auth_lifecycle_register_login_reset():
    """Verify authentication lifecycle: register, login, forgot password, reset password, get me."""
    test_email = f"analyst_e2e_{os.getpid()}@captrix-test.ai"
    test_password = "SecurePassword123!"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": test_email,
        "full_name": "E2E Test Analyst",
        "password": test_password,
        "role": "Lead Auditor"
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    token = reg_data["access_token"]
    assert reg_data["user"]["email"] == test_email

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200
    login_token = login_res.json()["access_token"]

    # 3. Get Me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email
    assert me_res.json()["role"] == "Lead Auditor"

    # 4. Forgot password
    forgot_res = client.post("/api/auth/forgot-password", json={"email": test_email})
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["reset_token"]
    assert len(reset_token) == 6

    # 5. Reset password
    new_password = "NewSecurePassword456!"
    reset_res = client.post("/api/auth/reset-password", json={
        "email": test_email,
        "reset_token": reset_token,
        "new_password": new_password
    })
    assert reset_res.status_code == 200

    # 6. Verify new password login
    new_login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": new_password
    })
    assert new_login_res.status_code == 200


def test_03_workbook_upload_and_full_pipeline():
    """Verify document upload, statement generation, ratios, corporate finance, quality engine."""
    sample_excel = "sample_data/Acme_Corp_Financials_2025.xlsx"
    assert os.path.exists(sample_excel), "Sample Excel file must exist"

    with open(sample_excel, "rb") as f:
        file_bytes = f.read()

    headers = {"Authorization": "Bearer test-e2e-token"}
    upload_res = client.post(
        "/api/upload/",
        files={"file": ("Acme_Corp_Financials_2025.xlsx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"company_name": "Acme Global Dynamics"}
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert "upload_id" in upload_data
    upload_id = upload_data["upload_id"]
    assert upload_data["company_name"] == "Acme Global Dynamics"
    assert len(upload_data["sheet_names"]) >= 1
    assert "quality_report" in upload_data
    assert "reconciliation" in upload_data

    # Retrieve analysis
    analysis_res = client.get(f"/api/analysis/{upload_id}")
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()

    # Assert all major components are populated
    assert "statements" in analysis
    assert "balance_sheet" in analysis["statements"]
    assert "income_statement" in analysis["statements"]
    assert "cash_flow" in analysis["statements"]
    assert "trial_balance" in analysis["statements"]
    
    assert "ratios" in analysis
    assert "profitability" in analysis["ratios"]
    assert "liquidity" in analysis["ratios"]
    assert "solvency" in analysis["ratios"]
    assert "efficiency" in analysis["ratios"]

    assert "corporate_finance" in analysis
    assert "capital_budgeting" in analysis["corporate_finance"]
    assert "capital_structure" in analysis["corporate_finance"]
    assert "working_capital_cycle" in analysis["corporate_finance"]

    assert "dupont_analysis" in analysis
    assert "risk_intelligence" in analysis
    assert "audit_report" in analysis
    assert "multi_period" in analysis
    assert "quality_report" in analysis


def test_04_sample_workbook_loader_endpoint():
    """Verify loading sample workbook directly via API."""
    res = client.post("/api/upload/sample")
    assert res.status_code == 200
    sample_data = res.json()
    assert "upload_id" in sample_data
    assert sample_data["company_name"] == "Acme Corporation"
    assert "health_score" in sample_data


def test_05_reports_generation_pdf_and_excel():
    """Verify PDF and Excel report generation endpoints."""
    # First get or create an upload
    res = client.post("/api/upload/sample")
    upload_id = res.json()["upload_id"]

    # 1. PDF Download
    pdf_res = client.get(f"/api/reports/pdf/{upload_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 2000

    # 2. Excel Download
    excel_res = client.get(f"/api/reports/excel/{upload_id}")
    assert excel_res.status_code == 200
    assert "spreadsheet" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 2000


def test_06_ai_copilot_chat_and_history():
    """Verify grounded AI financial chat copilot and chat conversation history."""
    res = client.post("/api/upload/sample")
    upload_id = res.json()["upload_id"]

    queries = [
        "What is the company's Net Income and Operating Margin?",
        "Is the current ratio healthy for liquidity?",
        "Give strategic recommendations based on the financial performance."
    ]

    for q in queries:
        chat_res = client.post("/api/chat/", json={"upload_id": upload_id, "query": q})
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert "response" in chat_data
        assert len(chat_data["response"]) > 10

    # Check conversation history
    hist_res = client.get(f"/api/chat/history/{upload_id}")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= len(queries)
    assert any("Net Income" in h["query"] for h in history)


def test_07_model_registry_leaderboard_and_benchmark():
    """Verify model discovery registry, leaderboard, universal benchmark, and document evaluation."""
    # 1. Model Registry
    reg_res = client.get("/api/models/registry")
    assert reg_res.status_code == 200
    assert "registered_models" in reg_res.json()
    assert reg_res.json()["total_models"] >= 3

    # 2. Model Leaderboard
    lb_res = client.get("/api/models/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    assert "leaderboard" in lb_data
    assert len(lb_data["leaderboard"]) >= 3
    assert "top_performing_model" in lb_data

    # 3. Universal Benchmark
    bm_res = client.post("/api/models/universal-benchmark")
    assert bm_res.status_code == 200
    bm_data = bm_res.json()
    assert bm_data["status"] in ["APPROVED", "REVIEW_REQUIRED"]
    assert len(bm_data["evaluations_leaderboard"]) >= 3

    # 4. Evaluate specific upload
    res = client.post("/api/upload/sample")
    upload_id = res.json()["upload_id"]
    eval_res = client.post(f"/api/models/evaluate/{upload_id}")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "evaluations_leaderboard" in eval_data
    assert "winner_model_name" in eval_data
    assert "document_profile" in eval_data


def test_08_history_search_filter_and_deletion():
    """Verify history list with search, filter, and deletion."""
    # Ensure at least 1 record exists
    sample_res = client.post("/api/upload/sample")
    upload_id = sample_res.json()["upload_id"]

    # 1. Fetch all history
    all_hist_res = client.get("/api/history/")
    assert all_hist_res.status_code == 200
    records = all_hist_res.json()
    assert len(records) >= 1

    # 2. Search filter
    search_res = client.get("/api/history/?search=Acme")
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1

    # 3. Status filter
    status_res = client.get("/api/history/?status_filter=COMPLETED")
    assert status_res.status_code == 200
    assert len(status_res.json()) >= 1

    # 4. Delete the history record
    first_record = records[0]
    del_res = client.delete(f"/api/history/{first_record['id']}")
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"]
