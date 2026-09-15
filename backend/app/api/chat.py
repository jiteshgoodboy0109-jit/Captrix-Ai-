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

@router.post("")
@router.post("/")
def chat_with_financial_ai(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.engine.authoritative_pipeline import build_authoritative_analysis_payload
    payload, company_name, currency, sym = build_authoritative_analysis_payload(req.upload_id, db, current_user)
    statements_dict = payload.get("statements", {})
    ratios_dict = payload.get("ratios", {})
    corp_dict = payload.get("corporate_finance", {})
    ai_report_dict = payload.get("ai_report", {})

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
