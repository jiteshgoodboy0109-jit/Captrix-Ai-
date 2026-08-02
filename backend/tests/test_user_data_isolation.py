import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token
from app.db.database import get_db, Base, engine
from app.db.models import User, Upload, History

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

def test_user_data_isolation_and_privacy():
    # 1. Create two separate user accounts in the database
    token_user1 = create_access_token({"sub": "alice@company.com"})
    token_user2 = create_access_token({"sub": "bob@enterprise.org"})

    headers1 = {"Authorization": f"Bearer {token_user1}"}
    headers2 = {"Authorization": f"Bearer {token_user2}"}

    # 2. Alice uploads a sample financial workbook
    sample_path = os.path.join("sample_data", "Acme_Corp_Financials_2025.xlsx")
    if not os.path.exists(sample_path):
        from sample_data.create_sample_excel import generate_sample_workbook
        generate_sample_workbook()

    with open(sample_path, "rb") as f:
        res1 = client.post(
            "/api/upload/",
            headers=headers1,
            files={"file": ("Alice_Financials.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"company_name": "Alice Private Corp"}
        )
    
    assert res1.status_code == 200
    upload_id_alice = res1.json()["upload_id"]

    # 3. Verify Alice can access her upload, analysis, history, and PDF report
    res_alice_hist = client.get("/api/history/", headers=headers1)
    assert res_alice_hist.status_code == 200
    alice_hist_ids = [r["upload_id"] for r in res_alice_hist.json()]
    assert upload_id_alice in alice_hist_ids

    res_alice_analysis = client.get(f"/api/analysis/{upload_id_alice}", headers=headers1)
    assert res_alice_analysis.status_code == 200
    assert res_alice_analysis.json()["company_name"] == "Alice Private Corp"

    # 4. PRIVACY TEST: Bob logs in and attempts to access Alice's data
    # 4a. Bob's History must NOT include Alice's reports
    res_bob_hist = client.get("/api/history/", headers=headers2)
    assert res_bob_hist.status_code == 200
    bob_hist_ids = [r["upload_id"] for r in res_bob_hist.json()]
    assert upload_id_alice not in bob_hist_ids, "SECURITY FAILURE: Bob can see Alice's history!"

    # 4b. Bob tries to directly query Alice's analysis -> Must be denied (404/403)
    res_bob_analysis = client.get(f"/api/analysis/{upload_id_alice}", headers=headers2)
    assert res_bob_analysis.status_code == 404, "SECURITY FAILURE: Bob accessed Alice's analysis!"

    # 4c. Bob tries to download Alice's PDF report -> Must be denied (404/403)
    res_bob_pdf = client.get(f"/api/reports/pdf/{upload_id_alice}", headers=headers2)
    assert res_bob_pdf.status_code == 404, "SECURITY FAILURE: Bob downloaded Alice's PDF report!"

    # 4d. Bob tries to prompt AI Chatbot on Alice's upload -> Must be denied (404/403)
    res_bob_chat = client.post("/api/chat/", headers=headers2, json={"upload_id": upload_id_alice, "query": "Show revenue"})
    assert res_bob_chat.status_code in [404, 403], "SECURITY FAILURE: Bob prompted AI on Alice's data!"

    # 4e. Bob tries to delete Alice's history record -> Must be denied
    alice_hist_record_id = res_alice_hist.json()[0]["id"]
    res_bob_del = client.delete(f"/api/history/{alice_hist_record_id}", headers=headers2)
    assert res_bob_del.status_code == 404, "SECURITY FAILURE: Bob deleted Alice's history record!"

    print("\n✅ USER DATA ISOLATION TEST PASSED CLEANLY! Zero data leak between users.")
