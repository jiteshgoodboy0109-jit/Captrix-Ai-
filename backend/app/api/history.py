from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import History, Upload, User
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/api/history", tags=["History Module"])

@router.get("")
@router.get("/")
def get_history_list(
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce strict user-level data isolation
    query = db.query(History).filter(History.user_id == current_user.id).order_by(History.timestamp.desc())

    if search:
        query = query.filter(History.company_name.ilike(f"%{search}%") | History.report_name.ilike(f"%{search}%"))

    if status_filter:
        query = query.filter(History.status == status_filter)

    records = query.all()
    return [
        {
            "id": r.id,
            "upload_id": r.upload_id,
            "company_name": r.company_name,
            "health_score": r.health_score,
            "status": r.status,
            "report_name": r.report_name,
            "timestamp": r.timestamp
        }
        for r in records
    ]

@router.delete("/{history_id}")
def delete_history_record(history_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = db.query(History).filter(History.id == history_id, History.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="History record not found or access denied.")

    # Delete underlying upload belonging to current_user
    upload = db.query(Upload).filter(Upload.id == rec.upload_id, Upload.user_id == current_user.id).first()
    if upload:
        db.delete(upload)

    db.delete(rec)
    db.commit()
    return {"message": "History record deleted successfully."}
