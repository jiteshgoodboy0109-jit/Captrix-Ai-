import secrets
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.auth.jwt import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "Analyst"

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_token: str
    new_password: str

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    if not req.full_name or len(req.full_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters.")
    if not req.password or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    existing = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists. Please sign in instead.")
    
    hashed_pwd = get_password_hash(req.password)
    user = User(
        email=req.email.strip().lower(),
        full_name=req.full_name.strip(),
        password_hash=hashed_pwd,
        role=req.role or "Analyst"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        },
        "message": "Registration successful! Welcome to FinIntell AI."
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please verify credentials and try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        },
        "message": f"Welcome back, {user.full_name}!"
    }

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No registered account found with this email address.")
    
    # Generate a 6-digit secure PIN token
    pin = f"{secrets.randbelow(900000) + 100000}"
    user.reset_token = pin
    user.reset_token_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.commit()

    return {
        "message": f"Password reset security code generated and sent to {clean_email}.",
        "reset_token": pin,
        "email": clean_email
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    if not user.reset_token or user.reset_token != req.reset_token.strip():
        raise HTTPException(status_code=400, detail="Invalid security reset code.")

    if user.reset_token_expires and datetime.datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Reset security code has expired. Please request a new code.")

    if not req.new_password or len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long.")

    user.password_hash = get_password_hash(req.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {
        "message": "Password successfully updated! You may now sign in with your new password."
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at
    }
