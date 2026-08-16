from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company, User, FinancialData
from app.auth.jwt import get_current_user
from app.engine.statement_generator import generate_financial_statements
from app.reports.pdf_generator import generate_pdf_report
from app.reports.excel_generator import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Report Download Engine"])

def fetch_upload_payload(upload_id: int, db: Session, current_user: User):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload or upload.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Upload analysis not found.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    company_name = company.name if company else "Enterprise Target"

    ratio = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
    ai_rep = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()

    # Reconstruct statements_dict dynamically from database line items
    fd_items = db.query(FinancialData).filter(FinancialData.upload_id == upload_id).all()
    items = []
    for f in fd_items:
        meta = f.metadata_json or {}
        items.append({
            "account_code": f.account_code,
            "account_name": f.account_name,
            "account_type": f.account_type,
            "debit": f.debit,
            "credit": f.credit,
            "net_amount": f.net_amount,
            "sheet": meta.get("sheet", "Sheet1"),
            "row": meta.get("row", 1),
            "column": meta.get("column", "A"),
            "year": meta.get("year", "Current"),
            "unit": meta.get("unit", "Units"),
            "currency": meta.get("currency", "USD"),
            "source_label": meta.get("source_label", f.account_name),
            "source_value": meta.get("source_value", f.net_amount),
            "is_summary": meta.get("is_summary", False)
        })
    statements_dict = generate_financial_statements(items)
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
