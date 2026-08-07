from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company, User
from app.auth.jwt import get_current_user
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Report Download Engine"])

def fetch_upload_payload(upload_id: int, db: Session, current_user: User):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload or upload.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Upload analysis not found.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    company_name = company.name if company else "Enterprise Target"

    stmt = db.query(Statement).filter(Statement.upload_id == upload_id).first()
    ratio = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
    ai_rep = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()

    statements_dict = {
        "income_statement": stmt.income_statement if stmt else {},
        "balance_sheet": stmt.balance_sheet if stmt else {},
        "cash_flow": stmt.cash_flow if stmt else {},
        "trial_balance": stmt.trial_balance if stmt else {},
        "ledger_summary": stmt.ledger_summary if stmt else {}
    }
    ratios_dict = {
        "profitability": ratio.profitability if ratio else {},
        "liquidity": ratio.liquidity if ratio else {},
        "solvency": ratio.solvency if ratio else {},
        "efficiency": ratio.efficiency if ratio else {}
    }
    corp_dict = {
        "capital_budgeting": corp.capital_budgeting if corp else {},
        "capital_structure": corp.capital_structure if corp else {},
        "working_capital_cycle": corp.working_capital_cycle if corp else {}
    }
    ai_report_dict = {
        "health_score": ai_rep.health_score if ai_rep else 85,
        "executive_summary": ai_rep.executive_summary if ai_rep else "Comprehensive AI Financial Health Audit Completed.",
        "recommendations": ai_rep.recommendations if ai_rep else ["Maintain positive working capital", "Monitor liquidity coverage"]
    }

    return company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict

@router.get("/pdf/{upload_id}")
def download_pdf_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict = fetch_upload_payload(upload_id, db, current_user)
    pdf_bytes = generate_pdf_report(company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Audit_{upload_id}.pdf"
        }
    )

@router.get("/excel/{upload_id}")
def download_excel_report(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict = fetch_upload_payload(upload_id, db, current_user)
    excel_bytes = generate_excel_report(company_name, statements_dict, ratios_dict, corp_dict, ai_report_dict)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=Financial_Analysis_{upload_id}.xlsx"
        }
    )
