from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.jwt import get_current_user, User
from app.engine.authoritative_pipeline import build_authoritative_analysis_payload

router = APIRouter(prefix="/api/analysis", tags=["Financial Analysis"])

@router.get("/{upload_id}")
def get_analysis_results(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payload, company_name, doc_currency, sym = build_authoritative_analysis_payload(upload_id, db, current_user)
    return payload

