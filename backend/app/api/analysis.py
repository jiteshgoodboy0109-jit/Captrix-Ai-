from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, Company
from app.auth.jwt import get_current_user, User
from app.engine.multi_period_analyzer import generate_multi_period_analysis

router = APIRouter(prefix="/api/analysis", tags=["Financial Analysis"])

@router.get("/{upload_id}")
def get_analysis_results(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Enforce strict user-level data isolation
    upload = db.query(Upload).filter(Upload.id == upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload analysis not found or access denied.")

    company = db.query(Company).filter(Company.id == upload.company_id).first()
    stmt = db.query(Statement).filter(Statement.upload_id == upload_id).first()
    ratio = db.query(Ratio).filter(Ratio.upload_id == upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == upload_id).first()
    ai_report = db.query(AIReport).filter(AIReport.upload_id == upload_id).first()

    if not stmt or not ratio or not corp or not ai_report:
        raise HTTPException(status_code=404, detail="Incomplete analysis data.")

    statements_payload = {
        "balance_sheet": stmt.balance_sheet,
        "income_statement": stmt.income_statement,
        "cash_flow": stmt.cash_flow,
        "trial_balance": stmt.trial_balance,
        "ledger_summary": stmt.ledger_summary
    }

    multi_period = generate_multi_period_analysis(statements_payload)

    return {
        "upload_id": upload.id,
        "company_name": company.name if company else "Enterprise Target",
        "filename": upload.filename,
        "sheet_names": upload.sheet_names,
        "created_at": upload.created_at,
        "statements": statements_payload,
        "multi_period": multi_period,
        "ratios": {
            "profitability": ratio.profitability,
            "liquidity": ratio.liquidity,
            "solvency": ratio.solvency,
            "efficiency": ratio.efficiency
        },
        "corporate_finance": {
            "capital_budgeting": corp.capital_budgeting,
            "capital_structure": corp.capital_structure,
            "working_capital_cycle": corp.working_capital_cycle
        },
        "ai_report": {
            "health_score": ai_report.health_score,
            "executive_summary": ai_report.executive_summary,
            "strengths": ai_report.strengths,
            "weaknesses": ai_report.weaknesses,
            "recommendations": ai_report.recommendations
        }
    }
