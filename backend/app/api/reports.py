from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.jwt import get_current_user, User
from app.engine.authoritative_pipeline import build_authoritative_analysis_payload
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Report Download Engine"])

def fetch_upload_payload(upload_id: int, db: Session, current_user: User):
    payload, company_name, currency, sym = build_authoritative_analysis_payload(upload_id, db, current_user)
    statements_dict = payload.get("statements", {})
    ratios_dict = payload.get("ratios", {})
    corp_dict = payload.get("corporate_finance", {})
    ai_report_dict = payload.get("ai_report", {})
    audit_report = payload.get("audit_report", {})
    return company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict, audit_report, currency

@router.get("/pdf/{upload_id}")
@router.get("/{upload_id}/pdf")
def download_pdf_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payload, company_name, currency, sym = build_authoritative_analysis_payload(upload_id, db, current_user)
    pdf_bytes = generate_pdf_report(
        company_name=company_name,
        statements=payload.get("statements", {}),
        ratios=payload.get("ratios", {}),
        corp_fin=payload.get("corporate_finance", {}),
        ai_reports=payload.get("ai_report", {}),
        audit_report=payload.get("audit_report"),
        currency=currency,
        data_quality_warnings=payload.get("data_quality_warnings", [])
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Analysis_{upload_id}.pdf"
        }
    )

@router.get("/excel/{upload_id}")
@router.get("/{upload_id}/excel")
def download_excel_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payload, company_name, currency, sym = build_authoritative_analysis_payload(upload_id, db, current_user)
    excel_bytes = generate_excel_report(
        company_name=company_name,
        statements=payload.get("statements", {}),
        ratios=payload.get("ratios", {}),
        corp_fin=payload.get("corporate_finance", {}),
        ai_reports=payload.get("ai_report", {}),
        audit_report=payload.get("audit_report"),
        data_quality_warnings=payload.get("data_quality_warnings", [])
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Analysis_{upload_id}.xlsx"
        }
    )

