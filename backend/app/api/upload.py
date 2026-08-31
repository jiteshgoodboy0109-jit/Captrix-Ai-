import os
import traceback
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Company, Upload, FinancialData, Statement, Ratio, CorporateFinance, AIReport, History
from app.auth.jwt import get_current_user
from app.engine.document_parser import parse_workbook, sanitize_json_data, clean_value
from app.engine.statement_generator import generate_financial_statements
from app.engine.financial_analyzer import calculate_financial_ratios, calculate_corporate_finance
from app.engine.ai_insights import generate_ai_insights
from app.engine.canonical_model import build_canonical_dataset
from app.engine.reconciliation import perform_source_to_result_reconciliation
from app.engine.quality_engine import compute_financial_quality_score

router = APIRouter(prefix="/api/upload", tags=["Upload & AI Processing"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_company_name(filename: str, user_provided_name: str) -> str:
    """Extract clean company name from user input or automatically from the uploaded filename."""
    if user_provided_name and user_provided_name.strip() and user_provided_name.strip() not in ["Target Corporation", "Enterprise Company", "Acme Corporation"]:
        return user_provided_name.strip()

    # Auto-extract from filename (e.g. Tesla_Q4_Financials.pdf -> Tesla Q4)
    base = os.path.splitext(filename)[0]
    cleaned = base.replace("_", " ").replace("-", " ")
    blacklist = ["financials", "financial", "statement", "statements", "tb", "ledger", "2024", "2025", "2026", "v1", "v2", "final", "excel", "sheet", "pdf", "docx", "doc", "csv", "txt", "json", "word", "report"]
    words = [w.capitalize() for w in cleaned.split() if w.lower() not in blacklist]
    if words:
        return " ".join(words)
    return cleaned.title() or "Enterprise Target Entity"

from typing import Optional

@router.post("")
@router.post("/")
async def upload_financial_file(
    file: UploadFile = File(...),
    company_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size > 250 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds maximum 250MB limit.")

        # Auto-detect or sanitize company name
        filename = file.filename or "uploaded_document"
        final_company_name = extract_company_name(filename, company_name or "")

        # Save raw file locally
        saved_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{filename}")
        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # 1. AI Document Engine: Parse workbook
        parsed = parse_workbook(file_bytes, filename)
        sheet_names = parsed.get("sheet_names", [])
        items = parsed.get("normalized_items", [])
        detected_currency = parsed.get("currency", "USD") or "USD"

        if not items:
            raise HTTPException(status_code=400, detail="Could not extract valid financial data lines from document.")

        # 2. Company record with exact detected currency
        company = Company(name=final_company_name, industry="Enterprise Accounting", currency=detected_currency)
        db.add(company)
        db.commit()
        db.refresh(company)

        # 3. Create Upload record
        upload = Upload(
            user_id=current_user.id,
            company_id=company.id,
            filename=file.filename,
            file_path=saved_path,
            file_size=file_size,
            sheet_names=sheet_names,
            status="COMPLETED"
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        # 4. Save Financial Line Items (Fast Batch Bulk Insert)
        fd_records = []
        for item in items:
            fd = FinancialData(
                upload_id=upload.id,
                account_code=item.get("account_code", ""),
                account_name=item.get("account_name", "Account Item"),
                account_type=item.get("account_type", "ASSET"),
                debit=clean_value(item.get("debit", 0.0)),
                credit=clean_value(item.get("credit", 0.0)),
                net_amount=clean_value(item.get("net_amount", 0.0)),
                metadata_json={
                    "sheet": item.get("sheet", "Sheet1"),
                    "row": item.get("row", 1),
                    "column": item.get("column", "A"),
                    "year": item.get("year", "Current"),
                    "unit": item.get("unit", "Units"),
                    "currency": item.get("currency", "USD"),
                    "source_sheet": item.get("source_sheet") or item.get("sheet", "Sheet1"),
                    "source_cell": item.get("source_cell") or f"{item.get('column', 'A')}{item.get('row', 1)}",
                    "source_column": item.get("source_column") or item.get("column", "A"),
                    "source_row": item.get("source_row") or item.get("row", 1),
                    "source_header": item.get("source_header") or item.get("period_raw") or item.get("fiscal_year", ""),
                    "period_raw": item.get("period_raw") or item.get("source_header") or item.get("fiscal_year", ""),
                    "raw_value": item.get("raw_value") if item.get("raw_value") is not None else item.get("value", 0.0),
                    "source_label": item.get("source_label", item.get("account_name", "")),
                    "source_value": item.get("source_value", item.get("value", 0.0)),
                    "is_summary": item.get("is_summary", False),
                    "is_quarterly": item.get("is_quarterly", False),
                    "period_type": item.get("period_type", "ANNUAL"),
                    "fiscal_year": item.get("fiscal_year", ""),
                    "period_id": item.get("period_id", ""),
                    "scope": item.get("scope", "STANDALONE")
                }
            )
            fd_records.append(fd)
        if fd_records:
            db.add_all(fd_records)

        # 5. Financial Statement Engine
        statements = sanitize_json_data(generate_financial_statements(items))
        stmt_record = Statement(
            upload_id=upload.id,
            balance_sheet=statements.get("balance_sheet", {}),
            income_statement=statements.get("income_statement", {}),
            cash_flow=statements.get("cash_flow", {}),
            trial_balance=statements.get("trial_balance", {}),
            ledger_summary=statements.get("ledger_summary", {})
        )
        db.add(stmt_record)

        # 6. Ratio Analysis & Corporate Finance Engine
        ratios = sanitize_json_data(calculate_financial_ratios(statements))
        ratio_record = Ratio(
            upload_id=upload.id,
            profitability=ratios.get("profitability", {}),
            liquidity=ratios.get("liquidity", {}),
            solvency=ratios.get("solvency", {}),
            efficiency=ratios.get("efficiency", {})
        )
        db.add(ratio_record)

        corp_fin = sanitize_json_data(calculate_corporate_finance(statements, ratios))
        corp_record = CorporateFinance(
            upload_id=upload.id,
            capital_budgeting=corp_fin.get("capital_budgeting", {}),
            capital_structure=corp_fin.get("capital_structure", {}),
            working_capital_cycle=corp_fin.get("working_capital_cycle", {})
        )
        db.add(corp_record)

        # 7. Canonical Dataset, Reconciliation & Quality Engine
        canonical_dataset = sanitize_json_data(build_canonical_dataset(items, filename))
        reconciliation_report = sanitize_json_data(perform_source_to_result_reconciliation(canonical_dataset, statements, ratios))
        quality_report = sanitize_json_data(compute_financial_quality_score(reconciliation_report, statements.get("validation_report", {})))

        # 8. AI Insights & Health Score Engine
        ai_insights = sanitize_json_data(generate_ai_insights(statements, ratios, corp_fin, canonical_dataset, quality_report=quality_report))
        health_score = ai_insights.get("canonical_health_score", {}).get("score", quality_report.get("quality_score", 85.0))
        ai_record = AIReport(
            upload_id=upload.id,
            health_score=clean_value(health_score),
            executive_summary=ai_insights.get("executive_summary", ""),
            strengths=ai_insights.get("strengths", []),
            weaknesses=ai_insights.get("weaknesses", []),
            recommendations=ai_insights.get("recommendations", [])
        )
        db.add(ai_record)

        # 9. Save Report History record automatically
        history_record = History(
            user_id=current_user.id,
            upload_id=upload.id,
            company_name=final_company_name,
            health_score=clean_value(health_score),
            status="COMPLETED",
            report_name=f"{final_company_name} - Financial Audit Report"
        )
        db.add(history_record)

        db.commit()

        return {
            "upload_id": upload.id,
            "filename": file.filename,
            "company_name": final_company_name,
            "sheet_names": sheet_names,
            "health_score": clean_value(health_score),
            "quality_report": quality_report,
            "reconciliation": reconciliation_report,
            "message": "Workbook processed, reconciled, analyzed, and saved to Report History successfully."
        }
    except HTTPException as he:
        print(f"HTTPException in upload: {he.detail}")
        raise he
    except Exception as err:
        db.rollback()
        tb = traceback.format_exc()
        print("Upload processing exception caught:\n", tb)
        raise HTTPException(status_code=400, detail=f"Workbook processing error: {str(err)}")

@router.post("/sample")
async def load_sample_file(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        sample_path = os.path.join("sample_data", "Acme_Corp_Financials_2025.xlsx")
        if not os.path.exists(sample_path):
            from sample_data.create_sample_excel import generate_sample_workbook
            generate_sample_workbook()

        with open(sample_path, "rb") as f:
            file_bytes = f.read()

        filename = "Acme_Corp_Financials_2025.xlsx"
        company_name = "Acme Corporation"
        file_size = len(file_bytes)

        saved_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_sample_{filename}")
        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        parsed = parse_workbook(file_bytes, filename)
        sheet_names = parsed.get("sheet_names", [])
        items = parsed.get("normalized_items", [])

        company = Company(name=company_name, industry="Enterprise Accounting", currency="USD")
        db.add(company)
        db.commit()
        db.refresh(company)

        upload = Upload(
            user_id=current_user.id,
            company_id=company.id,
            filename=filename,
            file_path=saved_path,
            file_size=file_size,
            sheet_names=sheet_names,
            status="COMPLETED"
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        for item in items:
            fd = FinancialData(
                upload_id=upload.id,
                account_code=item.get("account_code", ""),
                account_name=item.get("account_name", "Account Item"),
                account_type=item.get("account_type", "ASSET"),
                debit=clean_value(item.get("debit", 0.0)),
                credit=clean_value(item.get("credit", 0.0)),
                net_amount=clean_value(item.get("net_amount", 0.0)),
                metadata_json={
                    "sheet": item.get("sheet", "Sheet1"),
                    "row": item.get("row", 1),
                    "column": item.get("column", "A"),
                    "year": item.get("year", "Current"),
                    "unit": item.get("unit", "Units"),
                    "currency": item.get("currency", "USD"),
                    "source_sheet": item.get("source_sheet") or item.get("sheet", "Sheet1"),
                    "source_cell": item.get("source_cell") or f"{item.get('column', 'A')}{item.get('row', 1)}",
                    "source_column": item.get("source_column") or item.get("column", "A"),
                    "source_row": item.get("source_row") or item.get("row", 1),
                    "source_header": item.get("source_header") or item.get("period_raw") or item.get("fiscal_year", ""),
                    "period_raw": item.get("period_raw") or item.get("source_header") or item.get("fiscal_year", ""),
                    "raw_value": item.get("raw_value") if item.get("raw_value") is not None else item.get("value", 0.0),
                    "source_label": item.get("source_label", item.get("account_name", "")),
                    "source_value": item.get("source_value", item.get("value", 0.0)),
                    "is_summary": item.get("is_summary", False),
                    "is_quarterly": item.get("is_quarterly", False),
                    "period_type": item.get("period_type", "ANNUAL"),
                    "fiscal_year": item.get("fiscal_year", ""),
                    "period_id": item.get("period_id", ""),
                    "scope": item.get("scope", "STANDALONE")
                }
            )
            db.add(fd)

        statements = sanitize_json_data(generate_financial_statements(items))
        stmt_record = Statement(
            upload_id=upload.id,
            balance_sheet=statements.get("balance_sheet", {}),
            income_statement=statements.get("income_statement", {}),
            cash_flow=statements.get("cash_flow", {}),
            trial_balance=statements.get("trial_balance", {}),
            ledger_summary=statements.get("ledger_summary", {})
        )
        db.add(stmt_record)

        ratios = sanitize_json_data(calculate_financial_ratios(statements))
        ratio_record = Ratio(
            upload_id=upload.id,
            profitability=ratios.get("profitability", {}),
            liquidity=ratios.get("liquidity", {}),
            solvency=ratios.get("solvency", {}),
            efficiency=ratios.get("efficiency", {})
        )
        db.add(ratio_record)

        corp_fin = sanitize_json_data(calculate_corporate_finance(statements, ratios))
        corp_record = CorporateFinance(
            upload_id=upload.id,
            capital_budgeting=corp_fin.get("capital_budgeting", {}),
            capital_structure=corp_fin.get("capital_structure", {}),
            working_capital_cycle=corp_fin.get("working_capital_cycle", {})
        )
        db.add(corp_record)

        canonical_dataset = sanitize_json_data(build_canonical_dataset(items, filename))
        reconciliation_report = sanitize_json_data(perform_source_to_result_reconciliation(canonical_dataset, statements, ratios))
        quality_report = sanitize_json_data(compute_financial_quality_score(reconciliation_report, statements.get("validation_report", {})))

        ai_insights = sanitize_json_data(generate_ai_insights(statements, ratios, corp_fin, canonical_dataset, quality_report=quality_report))
        health_score = ai_insights.get("canonical_health_score", {}).get("score", quality_report.get("quality_score", 85.0))
        ai_record = AIReport(
            upload_id=upload.id,
            health_score=clean_value(health_score),
            executive_summary=ai_insights.get("executive_summary", ""),
            strengths=ai_insights.get("strengths", []),
            weaknesses=ai_insights.get("weaknesses", []),
            recommendations=ai_insights.get("recommendations", [])
        )
        db.add(ai_record)

        history_record = History(
            user_id=current_user.id,
            upload_id=upload.id,
            company_name=company_name,
            health_score=clean_value(health_score),
            status="COMPLETED",
            report_name=f"{company_name} - Financial Audit Report"
        )
        db.add(history_record)
        db.commit()

        return {
            "upload_id": upload.id,
            "filename": filename,
            "company_name": company_name,
            "sheet_names": sheet_names,
            "health_score": clean_value(health_score),
            "message": "Sample workbook loaded and saved to history."
        }
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Sample workbook error: {str(err)}")
