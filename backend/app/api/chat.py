from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Upload, Statement, Ratio, CorporateFinance, AIReport, ChatHistory, User
from app.auth.jwt import get_current_user
from app.engine.ai_insights import answer_financial_query

router = APIRouter(prefix="/api/chat", tags=["AI Copilot Chatbot"])

class ChatRequest(BaseModel):
    upload_id: int
    query: str

@router.post("/")
def chat_with_financial_ai(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload = db.query(Upload).filter(Upload.id == req.upload_id, Upload.user_id == current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload analysis context not found or access denied.")

    stmt = db.query(Statement).filter(Statement.upload_id == req.upload_id).first()
    ratio = db.query(Ratio).filter(Ratio.upload_id == req.upload_id).first()
    corp = db.query(CorporateFinance).filter(CorporateFinance.upload_id == req.upload_id).first()
    ai_rep = db.query(AIReport).filter(AIReport.upload_id == req.upload_id).first()

    if not stmt or not ratio or not corp or not ai_rep:
        raise HTTPException(status_code=400, detail="Financial data for this upload is incomplete.")

    statements_dict = {
        "income_statement": stmt.income_statement,
        "balance_sheet": stmt.balance_sheet,
        "cash_flow": stmt.cash_flow
    }
    ratios_dict = {
        "profitability": ratio.profitability,
        "liquidity": ratio.liquidity,
        "solvency": ratio.solvency,
        "efficiency": ratio.efficiency
    }
    corp_dict = {
        "capital_budgeting": corp.capital_budgeting,
        "capital_structure": corp.capital_structure,
        "working_capital_cycle": corp.working_capital_cycle
    }
    ai_report_dict = {
        "health_score": ai_rep.health_score,
        "executive_summary": ai_rep.executive_summary,
        "recommendations": ai_rep.recommendations
    }

    # Generate grounded response
    response_text = answer_financial_query(req.query, statements_dict, ratios_dict, corp_dict, ai_report_dict)

    # Persist chat log
    chat_log = ChatHistory(
        upload_id=req.upload_id,
        user_id=current_user.id,
        query=req.query,
        response=response_text
    )
    db.add(chat_log)
    db.commit()

    return {
        "query": req.query,
        "response": response_text
    }

@router.get("/history/{upload_id}")
def get_chat_history(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chats = db.query(ChatHistory).filter(ChatHistory.upload_id == upload_id, ChatHistory.user_id == current_user.id).order_by(ChatHistory.timestamp.asc()).all()
    return [
        {
            "id": c.id,
            "query": c.query,
            "response": c.response,
            "timestamp": c.timestamp
        }
        for c in chats
    ]
