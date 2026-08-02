import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def debug_upload():
    sample_path = os.path.join("sample_data", "Acme_Corp_Financials_2025.xlsx")
    if not os.path.exists(sample_path):
        from sample_data.create_sample_excel import generate_sample_workbook
        generate_sample_workbook()

    print("--- TESTING POST /api/upload/ ---")
    with open(sample_path, "rb") as f:
        # 1. Test with company_name provided
        res1 = client.post(
            "/api/upload/",
            files={"file": ("Acme_Corp_Financials_2025.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"company_name": "Test Company"}
        )
        print(f"Test 1 Status Code: {res1.status_code}")
        print(f"Test 1 Response: {res1.text}")

    with open(sample_path, "rb") as f:
        # 2. Test with empty data
        res2 = client.post(
            "/api/upload/",
            files={"file": ("Acme_Corp_Financials_2025.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        print(f"Test 2 Status Code: {res2.status_code}")
        print(f"Test 2 Response: {res2.text}")

if __name__ == "__main__":
    debug_upload()
